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
name = input("App to open: ").lower()
if name in APPS:
    target = APPS[name]
    if target.startswith("http"):
        webbrowser.open(target)
    else:
        os.startfile(target)
    print(f"Opening {name}...")
else:
    print("Unknown app.")
