"""Rule-based commands.

Every function returns a string (never crashes the loop), so these
survive whichever routing design is chosen later.
"""

from datetime import datetime
from pathlib import Path
from urllib.parse import quote
import webbrowser
import os
import sys

APPS = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "github": "https://github.com/leon-samuel-codes",
    "notepad": "notepad.exe",
    "spotify": r"C:\Users\Leon\AppData\Roaming\Spotify\Spotify.exe",
    "freebuff": "https://freebuff.com/chat",
}

# Phase R item 4: anchor runtime files to THIS file's folder.
BASE_DIR = Path(__file__).resolve().parent
PID_FILE = str(BASE_DIR / "server.pid")


def show_help():
    return """Available commands:
  facts                - show everything FRIDAY remembers
  remember <k>=<v>     - store a fact
  forget <key.path>    - remove a fact
  time / date          - current time/date
  open <app>           - launch an app
  search <query>       - web search
  github <owner/repo>  - repo info from the GitHub API
  define <word>        - dictionary definition
  ask <question>       - search the live web, then answer from the results
  system               - CPU, RAM and disk usage
  server start <cmd>   - start a background task, save its PID
  server stop          - stop the saved task
  killport <n>         - kill the process on port n
  media <play|next|prev> - control the music player
  mode <name>          - switch an action mode (Phase 12)
  /new                 - start a fresh conversation
  /voice               - turn spoken replies on/off (Phase 10)
  /listen              - speak instead of typing (push-to-talk)
  /telegram            - run the Telegram remote control (Phase 13)
  /hud                 - show the PyQt5 HUD overlay (Phase 14)
  help                 - this list
  exit                 - quit FRIDAY"""


def get_time():
    return datetime.now().strftime("%I:%M:%S %p")


def get_date():
    return datetime.now().strftime("%A, %d %B %Y")


def open_app(name):
    if name in APPS:
        target = APPS[name]
        if target.startswith("http"):
            webbrowser.open(target)
            return f"Opening {name}..."
        if sys.platform != "win32":                 # Phase R item 5
            return "Can only open apps by path on Windows."
        try:                                        # Phase R item 2
            os.startfile(target)
        except OSError as err:
            return f"Couldn't open {name} ({err})."
        return f"Opening {name}..."
    return f"I don't know how to open '{name}' yet."


def search_web(query):
    # Phase R item 3: quote() makes spaces and symbols URL-safe
    webbrowser.open(f"https://www.google.com/search?q={quote(query)}")
    return f"Searching for '{query}'..."


# -- Phase 7: external data (requests + free APIs, no key needed) ---

def github_lookup(repo):
    """Repo info from the GitHub REST API, e.g. 'github octocat/Hello-World'."""
    try:
        import requests
    except ImportError:
        return "Needs the 'requests' package — run: pip install requests"
    try:
        response = requests.get(f"https://api.github.com/repos/{repo}", timeout=10)
        if response.status_code == 404:
            return f"No GitHub repo found at '{repo}'."
        response.raise_for_status()
        data = response.json()
        return (
            f"{data.get('full_name', repo)} — "
            f"⭐ {data.get('stargazers_count', 0)} stars, "
            f"🍴 {data.get('forks_count', 0)} forks. "
            f"{data.get('description') or 'No description.'}"
        )
    except requests.RequestException as err:
        return f"Couldn't reach GitHub ({err})."
    except (KeyError, ValueError) as err:
        return f"Odd response from GitHub ({err})."


def define(word):
    """Dictionary definition from the free dictionaryapi.dev."""
    try:
        import requests
    except ImportError:
        return "Needs the 'requests' package — run: pip install requests"
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word)}"
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return f"No dictionary entry found for '{word}'."
        response.raise_for_status()
        entry = response.json()[0]
        definition = entry["meanings"][0]["definitions"][0]["definition"]
        return f"{entry.get('word', word)}: {definition}"
    except requests.RequestException as err:
        return f"Couldn't reach the dictionary ({err})."
    except (KeyError, IndexError, ValueError):
        return f"No definition found for '{word}'."


def ask(question):
    """Live web search results — main() puts them into the prompt so
    FRIDAY answers from current data instead of the model's old memory."""
    try:
        from ddgs import DDGS                # the package's new name
    except ImportError:
        try:
            from duckduckgo_search import DDGS   # old name still works
        except ImportError:
            return "Needs the 'ddgs' package — run: pip install ddgs"
    try:
        with DDGS() as ddgs:
            results = ddgs.text(question, max_results=5)
        if not results:
            return "The search came back empty."
        lines = [f"{i + 1}. {r.get('title', '')}: {r.get('body', '')}"
                 for i, r in enumerate(results)]
        return "\n".join(lines)
    except Exception as err:
        return f"Search failed ({err})."


# -- Phase 8: system tools --------------------------------------------

def system_stats():
    """CPU, RAM and disk usage via psutil."""
    try:
        import psutil
    except ImportError:
        return "Needs the 'psutil' package — run: pip install psutil"
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    gb = 1024 ** 3
    return (
        f"CPU: {cpu}% | RAM: {ram.percent}% ({ram.used // gb}/{ram.total // gb} GB) | "
        f"Disk: {disk.percent}% used"
    )


# -- Phase 8: start/stop your own server, kill by port ----

def server_start(shell_command):
    """Start a background task and save its PID to server.pid."""
    if not shell_command:
        return "Usage: server start <command>"
    import subprocess
    try:
        proc = subprocess.Popen(shell_command, shell=True,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
    except OSError as err:
        return f"Couldn't start it ({err})."
    try:
        with open(PID_FILE, "w", encoding="utf-8") as file:
            file.write(str(proc.pid))
    except OSError:
        pass
    return f"Started in the background (PID {proc.pid}). Stop it with 'server stop'."


def server_stop():
    """Stop the task whose PID is saved in server.pid."""
    import signal
    try:
        with open(PID_FILE, "r", encoding="utf-8") as file:
            pid = int(file.read().strip())
    except (FileNotFoundError, ValueError, OSError):
        return "No saved server to stop."
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return f"No process with PID {pid} — forgetting it."
    except PermissionError:
        return f"Not allowed to stop PID {pid}."
    except OSError as err:
        return f"Couldn't stop PID {pid} ({err})."
    try:
        os.remove(PID_FILE)
    except OSError:
        pass
    return f"Stopped PID {pid}."


def kill_port(port_text):
    """Kill whatever process is listening on a port (psutil)."""
    try:
        port = int(port_text)
    except (TypeError, ValueError):
        return "Usage: killport <port number>"
    try:
        import psutil
    except ImportError:
        return "Needs the 'psutil' package — run: pip install psutil"
    pids = set()
    for conn in psutil.net_connections():
        if getattr(conn.laddr, "port", None) == port and conn.pid:
            pids.add(conn.pid)
    if not pids:
        return f"Nothing is listening on port {port}."
    for pid in pids:
        try:
            psutil.Process(pid).terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            return f"Couldn't stop process {pid} (may need admin)."
    return (f"Killed on port {port}: "
            + ", ".join(str(p) for p in sorted(pids)))


# -- Phase 12: media-key song control ------------------------

def media_key(action):
    """Send a media key: media play | next | prev."""
    try:
        import keyboard
    except ImportError:
        return "Needs the 'keyboard' package — run: pip install keyboard"
    keys = {"play": "play/pause media",
            "next": "next track",
            "prev": "previous track"}
    if action not in keys:
        return "Usage: media play | next | prev"
    try:
        keyboard.press_and_release(keys[action])
    except Exception as err:
        return f"Media key failed ({err}) — on Windows this may need admin."
    return f"Media: {action}"
