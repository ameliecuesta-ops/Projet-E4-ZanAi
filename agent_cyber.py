import re
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Connexion à la mémoire locale (Vérifie bien le nom du dossier ici)
llm = ChatOllama(model="llama3.2", temperature=0)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
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
"""



# Template pour les QUESTIONS
template_expert = """Tu es un expert en cybersécurité (ZanAI). Réponds à la question en utilisant le CONTEXTE (RAG).
CONTEXTE : {context}
QUESTION : {question}

CONSIGNE : Sois précis, cite l'ANSSI, le NIST ou le MITRE si les infos sont dans le contexte."""





# 3. Fonction pour choisir le bon prompt dynamiquement
def get_prompt(input_text):
    # Liste de mots-clés étendue pour détecter les logs Web et SQL
    log_keywords = ["sshd", "failed", "accepted", "http", "port", "get", "post", "union", "select", "1=1"]
    
    if any(word in input_text.lower() for word in log_keywords):
        return ChatPromptTemplate.from_template(template_logs)
    return ChatPromptTemplate.from_template(template_expert)





# 4. Interface utilisateur
print("\n" + "="*60)
print("🛡️  STATION D'ANALYSE CYBER - MODE INVESTIGATION ACTIVÉ")
print("\n[ASTUCE] Collez vos logs ou posez une question.")
print("Tapez 'FIN' sur une nouvelle ligne pour valider.")

while True:
    try:
        print("\n[LOG OU QUESTION] > ")
        lines = []
        while True:
            line = input()
            if line.upper() == "FIN": break
            if line.lower() in ["exit", "quitter"]: sys.exit()
            lines.append(line)
        
        user_input = "\n".join(lines).strip()
        if not user_input: continue

        # Détection du type (Logs vs Texte)
        nb_tentatives = user_input.count("Failed password")
        
        # On prépare la "query" enrichie pour l'IA
        if nb_tentatives > 0:
            query_enriched = f"{user_input}\n(Note système : {nb_tentatives} échecs détectés)"
        else:
            query_enriched = user_input

        # On reconstruit la chaîne avec le bon prompt à la volée
        current_prompt = get_prompt(user_input)
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | current_prompt
            | llm
            | StrOutputParser()
        )

        print(f"\n[Agent] Analyse en cours...")
        print("-" * 30)



        
	# --- PARTIE CRUCIALE : LANCER L'IA ET RÉCUPÉRER LE TEXTE ---
        full_response = ""
        for chunk in chain.stream(query_enriched):
            print(chunk, end="", flush=True)
            full_response += chunk  # On remplit la variable au fur et à mesure
        
        print("\n" + "-" * 30)





        # --- AJOUT DE LA LOGIQUE BLACKLIST ---
        # On cherche l'IP associée au mot ALERTE dans le texte généré
        # Pattern : Cherche "IP : [adresse]" suivi plus loin de "STATUT : ALERTE"
        alert_ips = re.findall(r"IP\s*:\s*(\d{1,3}(?:\.\d{1,3}){3}).*?STATUT\s*:\s*ALERTE", full_response, re.DOTALL | re.IGNORECASE)

        if alert_ips:
            # On ouvre le fichier en mode "a" (append / ajout)
            with open("blacklist.txt", "a") as f:
                for ip in set(alert_ips): # set() évite les doublons si l'IA répète l'IP
                    f.write(f"{ip}\n")
            print(f"✅ [SYSTÈME] {len(set(alert_ips))} IP(s) suspecte(s) ajoutée(s) à blacklist.txt")
        # -------------------------------------

    except KeyboardInterrupt:
        break



