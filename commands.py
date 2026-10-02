from datetime import datetime
import webbrowser
import os

APPS = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "github": "https://github.com/leon-samuel-codes",
    "notepad": "notepad.exe",
    "spotify": r"C:\Users\Leon\AppData\Roaming\Spotify\Spotify.exe",
    "freebuff": "https://freebuff.com/chat"
}
def show_help():
    print("""Available commands:
  facts              - show everything FRIDAY remembers
  forget <key.path>  - remove a specific fact
  remember <k>=<v>   - store a fact
  time / date        - current time/date
  open <app>         - launch an app
  search <query>     - web search
  help              - this list
  exit               - quit FRIDAY""")
def open_app(name):
    if name in APPS:
        target = APPS[name]
        if target.startswith("http"):
            webbrowser.open(target)
        else:
            os.startfile(target)
        return f"Opening {name}..."
    return f"I don't know how to open '{name}' yet."

def search_web(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching for '{query}'..."

def get_time():
    now = datetime.now()
    return now.strftime("%I:%M:%S %p")        # 

def get_date():
    now = datetime.now()
    return now.strftime("%A, %d %B %Y")

