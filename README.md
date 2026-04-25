# 1. Construire et démarrer les containers

# 2. PREMIÈRE FOIS UNIQUEMENT — télécharger les modèles dans Ollama
# Sur Windows, exécutez les deux commandes manuellement :

# 3. Vérifier que tout tourne

docker compose up -d
docker exec zanai_ollama ollama pull llama3.2
docker exec zanai_ollama ollama pull nomic-embed-text
docker compose logs -f

docker compose down


# 4. Les fois d'après

docker compose up
docker compose down