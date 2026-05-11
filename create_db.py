import os
import glob
import time
from rich.console import Console
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# ---------------------- VARIABLES ----------------------------
DB_PATH = "./chroma_db"                 # Dossier de la base de données
EMBEDDING_MODEL = "nomic-embed-text"    # Model d'embeddin choisi
SEPARATEUR = "\n" + "-"*30
CONSOLE = Console()
START_TIME = time.perf_counter()

# ---------- CONFIGURATION DES DÉCOUPAGES MARKDOWN ------------
headers_to_split_on = [
    ("#", "Titre 1"),
    ("##", "Titre 2"),
    ("###", "Titre 3"),
]
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

# 2. Découpage de sécurité pour les PDF/CSV ou les blocs Markdown trop longs
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800, 
    chunk_overlap=100
)

# -------------------- FONCTIONS -------------------------------
# Retourne une liste de Chunk
def ingest_MD(file_Path):
    with open(file_Path, 'r', encoding='utf-8') as f:
        text = f.read()
    md_docs = markdown_splitter.split_text(text)
    chunks = text_splitter.split_documents(md_docs)
    for chunk in chunks:
        header_path = " > ".join(
            v for k, v in sorted(chunk.metadata.items())
            if k.startswith("Header")
        )
        chunk.metadata["section"] = header_path
        chunk.metadata["source"]  = file_Path
    return chunks

def ingest_TXT(file_Path):
    with open(file_Path, 'r', encoding='utf-8') as f:
        text = f.read()
    txt_docs = markdown_splitter.split_text(text)
    return text_splitter.split_documents(txt_docs)

def ingest_PDF(file_Path):
    loader = PyPDFLoader(file_Path)
    pdf_docs = loader.load()
    return text_splitter.split_documents(pdf_docs)

def ingest_CSV(file_Path):
    loader = CSVLoader(file_Path, encoding='utf-8')
    return loader.load()

def ingest_Data(data_Path):
    if not check_Folder(data_Path):
        return []

    all_chunks = []
    for file_path in glob.glob(f"{data_Path}/*"):
        print(f"Lecture de : {file_path}...")
        extention = check_Extention(file_path)
        if extention is not None:
            chunks = extention(file_path)
            all_chunks.extend(chunks)

    if check_db_created(all_chunks):
        return all_chunks
    else :
        print("[ERREUR] : Les chunks n'ont pas été correctement créés")
        return []

def check_Folder(data_Path):
    if not os.path.exists(data_Path):
        print(f"[ERREUR] : Le dossier '{data_Path}' n'existe pas")
        return False
    return True

def check_Extention(file_Path):
    file_ext = os.path.splitext(file_Path)[1].lower()
    file_Extention = EXTENTIONS.get(file_ext)
    if file_Extention is None:
        print(f"[ERREUR] : Format non supporté ==> {file_Path}")
    return file_Extention

def check_db_created(all_chunks):
    if not all_chunks:
        print("[ERREUR] Aucun document valide trouvé. La base de données n'a pas été créée.")
        return False
    print(f"\n{len(all_chunks)} segments prêts à être vectorisés.")
    print(SEPARATEUR)
    print("Création de la base ChromaDB en cours (cela peut prendre quelques minutes)...")
    return True

def Vectorisation_et_save(all_chunks):
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    with CONSOLE.status("[bold green]Vectorisation et création de la base de données...", spinner="dots"):
        vectorstore = Chroma.from_documents(
            documents=all_chunks, 
            embedding=embeddings, 
            persist_directory=DB_PATH
        )
    CONSOLE.print(f"[bold blue]✅[/bold blue] [SUCCES] : Base de données sauvegardée dans '{DB_PATH}'")

def get_execution_time(start_time):
    end_time = time.perf_counter()
    duration = end_time - start_time
    minutes, seconds = divmod(duration, 60)
    if minutes > 0:
        print(f"BDD Créé en {int(minutes)} min et {int(seconds)} sec")
    else:
        print(f"BDD Créé en {duration:.2f} secondes")

# ------------------ DICTIONNAIRE -----------------------------

EXTENTIONS: dict[str, callable] = {
    ".md":  ingest_MD,
    ".txt": ingest_TXT,
    ".pdf": ingest_PDF,
    ".csv": ingest_CSV,
}

# --------------------- MAIN ------------------------------------
while True:
    try:
        print(SEPARATEUR)
        print("\nQuel est le nom du dossier contenant les données d'entraînement ?")
        print("[AIDE] 💡: Formats supportés ==> .txt, .md, .pdf et .csv")
        all_chunks = ingest_Data(input("> "))
        print('\n')
        Vectorisation_et_save(all_chunks)
        get_execution_time(START_TIME)
        print("Avez vous d'autre documents à ajouter ? OUI / NON")
        if input("> ") != "OUI":
            break    
    except KeyboardInterrupt:
        break