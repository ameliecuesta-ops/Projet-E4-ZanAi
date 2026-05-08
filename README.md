# ZanAI — Agent de Cybersécurité

ZanAI est un agent IA dédié à l'analyse de logs réseau. Il détecte automatiquement les comportements suspects (brute force SSH, injections SQL, anomalies volumétriques) en combinant un LLM local (Llama 3.2 via Ollama) et une base de connaissances RAG (ChromaDB). Une interface web Flask permet de dialoguer avec l'agent et de lancer des simulations d'attaques en temps réel.

---

## Stack technique

| Composant | Technologie |
|---|---|
| LLM | Llama 3.2 (Ollama) |
| Embeddings | nomic-embed-text (Ollama) |
| Mémoire vectorielle | ChromaDB |
| Backend | Flask (Python 3.11) |
| Orchestration | LangChain |
| Déploiement | Docker Compose |

---

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et [Docker Compose](https://docs.docker.com/compose/) installés
- ~5 Go d'espace disque libre (pour les modèles Ollama)

---

## Installation et premier lancement

> ⚠️ **La première fois uniquement**, les modèles LLM doivent être téléchargés manuellement dans le container Ollama. Suivre les étapes dans l'ordre.

**1. Démarrer les containers en arrière-plan**

```bash
docker compose up -d
```

Cela démarre deux services : `zanai_ollama` (le moteur LLM) et `zanai_flask` (l'application web). Cette étape peut prendre quelques minutes.

**2. Télécharger les modèles IA**

Une fois les containers démarrés, télécharger les deux modèles nécessaires :

```bash
docker exec zanai_ollama ollama pull llama3.2
docker exec zanai_ollama ollama pull nomic-embed-text
```

> Ces modèles sont stockés dans un volume Docker persistant (`ollama_data`). Cette étape n'est à faire **qu'une seule fois**.

**3. Suivre les logs de démarrage**

```bash
docker compose logs -f
```

L'application est prête lorsque le message `ZAN AI AGENT - Serveur démarré` apparaît. Accéder ensuite à [http://localhost:5000](http://localhost:5000).

---

## Utilisations suivantes

**Démarrer**

```bash
docker compose up --build
```

**Arrêter**

```bash
docker compose down
```

---

## Structure du projet

```
Projet-E4-ZanAi/
├── app.py                  # Serveur Flask — routes et API SSE
├── agent_cyber.py          # Agent LangChain — analyse des logs via RAG
├── simulation.py           # Moteur de simulation d'attaques réseau
├── load_rag.py             # Utilitaire de vérification de la base RAG
├── RAG.txt                 # Base de connaissances (règles, normes MITRE/ANSSI/NIST)
├── chroma_db/              # Base vectorielle ChromaDB (persistée)
├── templates/              # Pages HTML (index, chat, simulation, équipe)
├── static/                 # CSS par page
├── pull_models.sh          # Script alternatif pour télécharger les modèles
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Fonctionnalités

**Analyse de logs** — L'agent analyse des lignes de logs SSH ou HTTP et produit pour chaque IP un rapport structuré : statut (RAS / SUSPECT / ALERTE), règle déclenchée, motif, et liste des IPs à bloquer.

**Règles de détection**

| Règle | Condition | Gravité |
|---|---|---|
| R-001 | 5+ tentatives `Failed password` SSH pour une même IP | ALERTE |
| R-002 | 10+ codes HTTP 401/403 sur `/login` | SUSPECT |
| R-003 | Présence de signatures SQL (`UNION`, `SELECT`, `1=1`, `--`) | ALERTE |
| R-004 | 5+ lignes de logs pour une même IP (volumétrie) | ALERTE |

**Simulation** — Génère des logs réseau fictifs en temps réel (attaques brute force SSH, trafic légitime) et les soumet automatiquement à l'agent pour analyse.

**Interface chat** — Permet d'interroger l'agent librement sur des logs ou des questions de cybersécurité, avec historique de session et réponse en streaming.

---

## Variables d'environnement

| Variable | Valeur par défaut | Description |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | URL du service Ollama (défini automatiquement par Docker Compose) |