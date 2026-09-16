import json
def load_memory():
    try:
        with open("memory.json", "r") as file:
            data = json.load(file)
        if "facts" not in data:          
            data["facts"] = []
        return data
    except FileNotFoundError:
        return {"name": None, "facts": []}     
def save_memory(memory):
    with open("memory.json", "w") as file:
        json.dump(memory , file, indent=2)  