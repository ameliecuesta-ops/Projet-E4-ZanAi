# 🛡️ ZenAI: AI SOC Agent - Log Analysis & Local RAG 🛡️

ZenAI is a specialized Cybersecurity (SOC) AI agent designed to analyze system logs, detect ongoing attacks, and provide technical cybersecurity answers. The model is enhanced with **RAG (Retrieval-Augmented Generation)** to ensure high accuracy and context-aware responses.

This SOC Agent **RUNS ENTIRELY LOCALLY**, ensuring the **confidentiality** and privacy of the prompts and analyzed data.

## 🚀 Key Features

* **Customizable Training Dataset:** Adapt the agent to your specific environment by adding your own documents or company policies to the RAG context.
* **Automated Log Analysis:** Real-time classification of threats based on predefined security detection rules.
* **Dynamic Blacklisting:** Suspicious IP addresses (ALERT status) are automatically extracted and appended to a `blacklist.txt` file for remediation.
* **Privacy-First (100% Local):** All components are designed to run locally, preventing sensitive log data from leaving your infrastructure.

## 🧠 Architecture

The project leverages three core components:
* **Ollama:** Manages local AI models (`llama3.2` for reasoning and `nomic-embed-text` for vectorization).
* **LangChain:** Orchestrates the RAG pipeline, handles dynamic prompting, and manages the interface between the LLM and the database.
* **ChromaDB:** A high-performance vector database that stores the security context and rules, providing the agent with a reliable reference for analysis.

## 📄 File Structure
* `chroma_db/`: Folder containing the persistent vector database.
* `training_data/`: Directory for source files used to build the RAG context (.md, .txt, .pdf and .csv supported).
* `ZenAI.py`: The main AI agent script **[RUN THIS FILE]**.
* `create_db.py`: Ingestion script to process files from `/training_data` into ChromaDB.
* `check_db_content.py`: Utility script to inspect the current state and composition of the database.
* `blacklist.txt`: Automatically generated file containing banned IP addresses.

---

## 🛠️ Installation & Prerequisites

### System requirements
* **OS:** Windows 10/11, Linux, or MacOS.
### Software requirements
* **Python:** 3.10+ (Available at [python.org](https://www.python.org/downloads/)).
* **Ollama:** Locally installed (Available at [ollama.com](https://ollama.com/download)).

### ⚙️ Setup
Open your terminal and install the required Python packages:
```bash
pip install langchain-ollama langchain-chroma langchain-core langchain-community langchain-text-splitters pypdf
```
Then install the models : 
```bash
ollama pull llama3.2
```
```bash
ollama pull nomic-embed-text
```
You can now launch ZenAI
```
python3 ZenAI.py
```