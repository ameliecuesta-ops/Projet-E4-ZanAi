import re
import os
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Lit l'adresse Ollama depuis l'environnement (Docker) ou utilise localhost par défaut
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# 1. Connexion à la mémoire locale
llm = ChatOllama(model="llama3.2", temperature=0, base_url=OLLAMA_HOST)
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_HOST)
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})


# 2. DÉFINITION DU PROMPT (L'intelligence de l'agent)
# Template pour les LOGS
template_logs = """tu es un automate de sécurité binaire. Ne discute pas, ne justifie pas tes étapes.
IMPORTANT : Ne cite JAMAIS les adresses IP non présentes dans les LOGS À ANALYSER.


RAG (INTERDIT DE CITER CES IP) :
{context}

LOGS À ANALYSER (UTILISE UNIQUEMENT CES IP LA) :
{question}


INSTRUCTIONS :
1. FILTRE : Identifie les IPs uniques dans "LOGS À ANALYSER". Si une IP n'apparaît pas dans cette liste, elle est INTERDITE dans ta réponse. 
2. Si une IP est dans le RÉFÉRENTIEL mais PAS dans les LOGS -> IGNORE-LA TOTALEMENT.
3. si il y a plusieurs lignes de logs avec la meme adresse IP fait UN SEUL bloc de réponse par adresse IP. Ne recopie JAMAIS le bloc de logs entier dans ta réponse 
4. Cherche les signatures EXACTES : "UNION", "SELECT", "1=1", "--" ou "Failed password". Si aucun de ces termes n'est présent, l'IP ne peut PAS être en R-003 ou R-001
5. Si trouvée -> STATUT : ALERTE, RÈGLE : R-003 (SQL) ou R-001 (SSH).STOP : Ne passe pas à l'étape suivante pour cette IP.
6. ANALYSE VOLUMÉTRIQUE (Si pas de signature) : Compte les lignes :
    - 5+ lignes -> STATUT : ALERTE (R-004 uniquement)
    - 2-4 lignes -> SUSPECT
    - 0-1 ligne -> RAS



FORMAT DE REPONSE OBLIGATOIRE (un seul bloc par IP) :
---
IP : [Mettre l'IP ici]
STATUT : [Mettre ALERTE, SUSPECT ou RAS ici]
RÈGLE : [Mettre le numéro ici]
MOTIF : [Mettre la phrase ici]
---

A LA FIN DE LA REPONSE :
---
IPs A BLOQUER:
[Lister (sous forme de liste avec des tirets et un retour à la ligne pour chaque ip) les IPs en état ALERTE]
"""


# Template pour les QUESTIONS
template_expert = """Tu es un expert en cybersécurité (ZanAI). Réponds à la question en utilisant le CONTEXTE (RAG).
CONTEXTE : {context}
QUESTION : {question}

CONSIGNE : Sois précis, cite l'ANSSI, le NIST ou le MITRE si les infos sont dans le contexte."""

template_simulation = """Tu es un expert en cybersécurité (ZanAI). Réponds à la question en utilisant le CONTEXTE (RAG).
CONTEXTE : {context}
QUESTION : {question}

INSTRUCTIONS :
1. FILTRE : Identifie les IPs uniques dans "LOGS À ANALYSER". Si une IP n'apparaît pas dans cette liste, elle est INTERDITE dans ta réponse. 
2. Si une IP est dans le RÉFÉRENTIEL mais PAS dans les LOGS -> IGNORE-LA TOTALEMENT.
3. si il y a plusieurs lignes de logs avec la meme adresse IP fait UN SEUL bloc de réponse par adresse IP. Ne recopie JAMAIS le bloc de logs entier dans ta réponse 
4. Cherche les signatures EXACTES : "UNION", "SELECT", "1=1", "--" ou "Failed password". Si aucun de ces termes n'est présent, l'IP ne peut PAS être en R-003 ou R-001
5. Si trouvée -> STATUT : ALERTE, RÈGLE : R-003 (SQL) ou R-001 (SSH).STOP : Ne passe pas à l'étape suivante pour cette IP.
6. ANALYSE VOLUMÉTRIQUE (Si pas de signature) : Compte les lignes :
    - 5+ lignes -> STATUT : ALERTE (R-004 uniquement)
    - 2-4 lignes -> SUSPECT
    - 0-1 ligne -> RAS



FORMAT DE REPONSE OBLIGATOIRE
[Lister (sous forme de liste avec des tirets et un retour à la ligne pour chaque ip) les IPs en état ALERTE] """


# 3. Fonction pour choisir le bon prompt dynamiquement
def get_prompt(input_text):
    log_keywords = ["sshd", "failed", "accepted", "http", "port", "get", "post", "union", "select", "1=1"]
    simu_keyword = ["ADMINSIMULATION"]
    if any(word in input_text.lower() for word in simu_keyword):
        return ChatPromptTemplate.from_template(template_simulation)
    elif any(word in input_text.lower() for word in log_keywords):
        return ChatPromptTemplate.from_template(template_logs)
    return ChatPromptTemplate.from_template(template_expert)


# 4. Fonction streaming appelée par Flask (SSE)
def run_agent_stream(user_input: str):
    """
    Génère les chunks de la réponse au fur et à mesure.
    Yielde chaque morceau de texte, puis écrit la blacklist à la fin.
    """
    user_input = user_input.strip()
    if not user_input:
        return

    nb_tentatives = user_input.count("Failed password")
    query_enriched = (
        f"{user_input}\n(Note système : {nb_tentatives} échecs détectés)"
        if nb_tentatives > 0
        else user_input
    )

    current_prompt = get_prompt(user_input)
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | current_prompt
        | llm
        | StrOutputParser()
    )

    full_response = ""
    for chunk in chain.stream(query_enriched):
        full_response += chunk
        yield chunk  # envoie au front en temps réel

    # Blacklist après le stream complet
    alert_ips = re.findall(
        r"IP\s*:\s*(\d{1,3}(?:\.\d{1,3}){3}).*?STATUT\s*:\s*ALERTE",
        full_response,
        re.DOTALL | re.IGNORECASE
    )
    if alert_ips:
        with open("blacklist.txt", "a") as f:
            for ip in set(alert_ips):
                f.write(f"{ip}\n")


# 5. Fonction classique (conservée au cas où)
def run_agent(user_input: str) -> str:
    return "".join(run_agent_stream(user_input))