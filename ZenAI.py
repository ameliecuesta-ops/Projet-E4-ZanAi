import sys
import re
from templates import template_logs, template_expert
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ------------- CHARGEMENT DU MODELE ----------------
llm_Model = ChatOllama(model="llama3.2", temperature=0)     # Temps=0 pour reduire les halucinations
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# ------------------ VARIABLES -----------------------
agent_Mode = ""
helpMessage = "[AIDE] Tapez 'log' pour l'analyse de log, 'expert' pour le mode expert ou 'exit' pour quitter"
astuceMessage = "[ASTUCE] Tapez 'FIN' sur la dernière ligne pour valider."
Separateur = "\n" + "-"*30

# ------------------ FONCTIONS ------------------------
def get_Agent_Mode(): 
    print("\n" + "="*60)
    print("🛡️ AGENT SOC IA (ZanAI) 🛡️ - Analyse de logs et expert cyber")
    print("\n[CHOIX DU MODE]\n" + helpMessage)
    while True:
        user_Agent_input = input("Choix > ").lower().strip()
        match user_Agent_input:
            case "exit":
                print("Arrêt de l'agent IA")
                sys.exit()
            case "log":
                return "LOG"
            case "expert":
                return "EXPERT"
            case _:
                print("Je n'ai pas compris votre demande\n" + helpMessage)

def capture_user_Prompt_Input():
    lines = []
    while True:
        line = input("> ")
        if line.upper() == "FIN":  break
        if line.lower() in ["exit", "quitter"]: 
            print("Arrêt de ZenAI")
            sys.exit()
        lines.append(line)
    return "\n".join(lines).strip()

def enrich_query(user_input, agent_Mode):
    #Prépare la requête pour l'IA en ajoutant des métadonnées si nécessaire 
    query_final = user_input
    if agent_Mode == "LOG":
        # Détection automatique pour aider l'IA avec la règle R-001 
        nb_fail = user_input.count("Failed password")
        if nb_fail > 0:
            query_final += f"\n(Note système : {nb_fail} échecs de connexion détectés)"
    return query_final

def template_to_use(agent_Mode):
    if agent_Mode == "LOG":
        return  ChatPromptTemplate.from_template(template_logs)
    elif agent_Mode == "EXPERT":
        return ChatPromptTemplate.from_template(template_expert)
    else:
        print("Erreur lors du choix du template : Template inexistant")


def blacklist_IP(llm_response):
    pattern = r"IP\s*:\s*(\d{1,3}(?:\.\d{1,3}){3}).*?STATUT\s*:\s*ALERTE"
    alert_ips = re.findall(pattern, llm_response, re.DOTALL | re.IGNORECASE)

    if alert_ips:
        with open("blacklist.txt", "a") as f:
            for ip in set(alert_ips):
                f.write(f"{ip}\n")
        print(f"[SYSTÈME] {len(set(alert_ips))} IP(s) ajoutée(s) à blacklist.txt")

# -------------------- MAIN --------------------------
# Choix du mode à utiliser
agent_Mode = get_Agent_Mode()

while True:
    try:
        print("Mode sélectionné : " + agent_Mode)
        print(astuceMessage)
        # Récupération du prompt de l'utilisateur
        user_Promt_Input = capture_user_Prompt_Input()
        if not user_Promt_Input: continue

        # Enrichissement pour le mode LOG 
        query_final = enrich_query(user_Promt_Input, agent_Mode)

        # Exécution de la chaîne IA
        prompt = template_to_use(agent_Mode)
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm_Model
            | StrOutputParser()
        )
        print(f"\n[Agent] Analyse en cours...")
        print(Separateur)

        # Constuction de la réponse par chunk
        full_response = ""
        for chunk in chain.stream(query_final):
            print(chunk, end="", flush=True)
            full_response += chunk  # On remplit la variable au fur et à mesure
        print(Separateur)

        # Action post analyse 
        if agent_Mode == "LOG":
            blacklist_IP(full_response)

    except KeyboardInterrupt:
        break