#!/bin/bash
# Script à lancer UNE SEULE FOIS après le premier docker compose up
# Pour télécharger les modèles dans le container Ollama

echo "⏳ Téléchargement de llama3.2..."
docker exec zanai_ollama ollama pull llama3.2

echo "⏳ Téléchargement de nomic-embed-text..."
docker exec zanai_ollama ollama pull nomic-embed-text

echo "✅ Modèles prêts !"
