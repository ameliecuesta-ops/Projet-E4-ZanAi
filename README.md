# Premiere fois que vous faites tourner le docker sur votre ordi
Pour lancer (ca prends du temps c'est normal) :
- docker compose up -d
- docker exec zanai_ollama ollama pull llama3.2
- docker exec zanai_ollama ollama pull nomic-embed-text
- docker compose logs -f

Pour arreter :
- docker compose down


# Les fois d'après

Pour Lancer 
- docker compose up --build

Pour arreter
- docker compose down
