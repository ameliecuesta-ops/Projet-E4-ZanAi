from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent

# ton tool ML
from tools import detect_attacks


# --- transformer ta fonction en tool ---
@tool
def detect_bruteforce():
    """Analyse le dataset réseau et retourne les statistiques d'attaques."""
    return detect_attacks()


# --- modèle LLM ---
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# --- création agent ---
agent = create_agent(
    model=model,
    tools=[detect_bruteforce],
    system_prompt="Tu es un analyste SOC expert en cybersécurité."
)

# --- exécution ---
response = agent.invoke({
    "messages": [
        {"role": "user",
         "content": "Analyse le dataset et dis-moi combien d’attaques brute force sont détectées."}
    ]
})

print("\n✅ Réponse finale :")
print(response["messages"][-1].content)
