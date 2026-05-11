from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# ---------------------- MAIN ----------------------------
print("🔎 ANALYSE DE LA BASE VECTORIELLE")
print("-" * 30)
DB_PATH = "./chroma_db"
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
all_data = vectorstore.get()
metadatas = all_data['metadatas']
documents = all_data['documents']

# ------------------ DATA DISPLAY ------------------------
total_Files = {"pdf": 0, "csv": 0, "md": 0, "txt": 0}
for i, meta in enumerate(metadatas):
    source = meta.get('source', '').lower()
    if source.endswith('.pdf'): total_Files['pdf'] += 1
    elif source.endswith('.csv'): total_Files['csv'] += 1
    elif source.endswith('.md'): total_Files['md'] += 1
    elif source.endswith('.txt'): total_Files['txt'] += 1

for ext, count in total_Files.items():
    print(f"📄 Fichiers {ext.upper()} : {count} segments trouvés.")

# CSV VIEW
print("\n💡 Aperçu d'un segment CSV :")
for i, meta in enumerate(metadatas):
    if meta.get('source', '').lower().endswith('.csv'):
        print(f"Source: {meta['source']}")
        print(f"Contenu: {documents[i][:200]}...\n") # Affiche le début de la ligne
        break