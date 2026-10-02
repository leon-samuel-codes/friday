import json
import os

MEMORY_FILE = "memory.json"
CORRUPT_FILE = "memory.corrupt.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        if "facts" not in data:
            data["facts"] = {}
        return data
    except FileNotFoundError:
        return {"name": None, "facts": {}}          
    except json.JSONDecodeError:
        print("⚠️  memory.json is corrupted — rescuing it as memory.corrupt.json")
        try:
            os.replace(MEMORY_FILE, CORRUPT_FILE)  
        except OSError:
            pass
        return {"name": None, "facts": {}}
    except OSError as err:
        print(f"⚠️  Couldn't read memory.json ({err}) — starting with empty memory.")
        return {"name": None, "facts": {}}

def save_memory(memory):
    tmp = MEMORY_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=2)
    os.replace(tmp, MEMORY_FILE)                    
