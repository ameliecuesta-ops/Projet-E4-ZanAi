# load_rag.py
# But : vérifier qu'on peut lire le RAG

rag_file = "RAG.txt"

with open(rag_file, "r", encoding="utf-8") as f:
    text = f.read()

# Vérifie que tout est bien lu
print(f"Longueur du RAG : {len(text)} caractères")
print("Aperçu du RAG :")
print(text[:500])  # affiche les 500 premiers caractères
