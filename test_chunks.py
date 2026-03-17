from langchain.text_splitters import RecursiveCharacterTextSplitter
import chromadb
import sentence_transformers
import ollama

# Test de LangChain
text = "Ceci est un exemple de texte que l'on veut découper en chunks."
splitter = RecursiveCharacterTextSplitter(chunk_size=10, chunk_overlap=2)
chunks = splitter.split_text(text)
print(chunks)
