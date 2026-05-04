import random
import re
import time
import threading
from datetime import datetime
from agent_cyber import run_agent_stream

# --- Fichiers ---
LOGS_FILE = "logs_simulation.txt"
ALERTES_FILE = "alerte_simulation.txt"

# --- Pool d'IPs simulées (quelques-unes reviendront souvent) ---
ATTACKER_IPS = [
    "192.168.1.45",   # reviendra souvent -> brute force
    "172.16.254.9",   # reviendra souvent -> brute force
    "203.0.113.77",   # reviendra souvent -> brute force
    "198.51.100.33",
    "45.33.32.156",
    "85.209.11.204",
    "91.108.4.200",
    "176.32.103.205",
]
LEGIT_IPS = ["10.0.0.5", "10.0.0.8", "10.0.0.12", "10.0.0.21"]
USERS = ["root", "admin", "ubuntu", "git", "deploy", "user", "alice", "bob"]

# --- État global de la simulation ---
_sim_thread = None
_sim_running = False
_sim_lock = threading.Lock()


def _generate_log_line() -> str:
    """Génère une ligne de log SSH aléatoire réaliste."""
    now = datetime.now().strftime("%b %d %H:%M:%S")
    pid = random.randint(1000, 9999)
    user = random.choice(USERS)
    port = random.randint(30000, 65000)

    # 70% de chances que ce soit une tentative échouée (attaquant)
    if random.random() < 0.70:
        ip = random.choice(ATTACKER_IPS)
        return f"{now} srv01 sshd[{pid}]: Failed password for {user} from {ip} port {port} ssh2"
    else:
        ip = random.choice(LEGIT_IPS)
        return f"{now} srv01 sshd[{pid}]: Accepted password for {user} from {ip} port {port} ssh2"


def _append_log(line: str):
    """Ajoute une ligne dans logs_simulation.txt."""
    with open(LOGS_FILE, "a") as f:
        f.write(line + "\n")


def _get_last_logs(n: int = 50) -> list[str]:
    """Retourne les n dernières lignes de logs_simulation.txt."""
    try:
        with open(LOGS_FILE, "r") as f:
            lines = [l.rstrip() for l in f.readlines() if l.strip()]
        return lines[-n:]
    except FileNotFoundError:
        return []


def _save_alert_ips(ips: list[str]):
    """Écrit les IPs ALERTE dans alerte_simulation.txt sans doublon."""
    existing = set()
    try:
        with open(ALERTES_FILE, "r") as f:
            existing = {l.strip() for l in f if l.strip()}
    except FileNotFoundError:
        pass

    new_ips = set(ips) - existing
    if new_ips:
        with open(ALERTES_FILE, "a") as f:
            for ip in sorted(new_ips):
                f.write(ip + "\n")


def _run_agent_on_logs(logs: list[str]) -> list[str]:
    """
    Appelle l'agent en mode ADMINSIMULATION avec les logs fournis.
    Retourne la liste des IPs à bannir extraites de la réponse.
    """
    logs_text = "\n".join(logs)
    prompt = f"ADMINSIMULATION\n{logs_text}"

    full_response = ""
    for chunk in run_agent_stream(prompt):
        full_response += chunk

    # Extrait toutes les IPs de la réponse (liste de tirets ou format IP brut)
    ips = re.findall(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b", full_response)
    return list(set(ips))


# Flag pour éviter de lancer plusieurs analyses en parallèle
_agent_running = False
_agent_lock = threading.Lock()


def _run_agent_async(logs: list):
    """Lance l'analyse de l'agent dans un thread séparé pour ne pas bloquer la boucle."""
    global _agent_running
    with _agent_lock:
        if _agent_running:
            return  # une analyse est déjà en cours, on skip
        _agent_running = True

    try:
        alert_ips = _run_agent_on_logs(logs)
        if alert_ips:
            _save_alert_ips(alert_ips)
    finally:
        with _agent_lock:
            _agent_running = False


def _simulation_loop(interval: int):
    """Boucle principale : génère des logs en continu, analyse en parallèle."""
    global _sim_running
    log_counter = 0

    while _sim_running:
        # Génère 1 à 3 lignes de logs à chaque tick
        for _ in range(random.randint(1, 3)):
            line = _generate_log_line()
            _append_log(line)
            log_counter += 1

        # Lance l'agent dans un thread séparé tous les 5 logs — sans bloquer
        if log_counter >= 5:
            log_counter = 0
            logs = _get_last_logs(50)
            if logs:
                threading.Thread(
                    target=_run_agent_async,
                    args=(logs,),
                    daemon=True
                ).start()

        time.sleep(interval)


# --- API publique ---

def start_simulation(interval: int = 15):
    """Démarre la simulation en arrière-plan. Sans effet si déjà active."""
    global _sim_thread, _sim_running
    with _sim_lock:
        if _sim_running:
            return False
        _sim_running = True
        _sim_thread = threading.Thread(
            target=_simulation_loop,
            args=(interval,),
            daemon=True
        )
        _sim_thread.start()
        return True


def stop_simulation():
    """Arrête la simulation."""
    global _sim_running
    with _sim_lock:
        if not _sim_running:
            return False
        _sim_running = False
        return True


def is_running() -> bool:
    return _sim_running


def get_status() -> dict:
    """Retourne l'état courant pour l'UI."""
    logs = _get_last_logs(50)

    alertes = []
    try:
        with open(ALERTES_FILE, "r") as f:
            alertes = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        pass

    return {
        "running": _sim_running,
        "log_count": len(logs),
        "last_logs": logs[-10:],   # 10 derniers pour l'affichage
        "alert_ips": alertes,
    }


def reset_files():
    """Vide les fichiers logs_simulation.txt et alerte_simulation.txt."""
    open(LOGS_FILE, 'w').close()
    open(ALERTES_FILE, 'w').close()
