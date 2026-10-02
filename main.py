import os, sys, time
import ollama
from ollama import chat
from ai import build_system_prompt, trim, format_facts

from memory import load_memory, save_memory
from commands import get_time, get_date, open_app, search_web,  show_help

THINK_TAG = "<" + "/" + "think" + ">"
MODEL = "qwen3:4b-instruct"



def check_ollama():
    try:
        ollama.list()
        return True
    except Exception:
        pass

    print("FRIDAY: Ollama isn't running — starting it...")
    ollama_path = os.path.join(os.environ["LOCALAPPDATA"],
                               "Programs", "Ollama", "Ollama.exe")
    try:
        os.startfile(ollama_path)
    except OSError:
        print("Couldn't find Ollama at:", ollama_path)
        return False

    for attempt in range(15):
        time.sleep(1)
        try:
            ollama.list()
            print("FRIDAY: Ollama ready.")
            return True
        except Exception:
            print(f"Waiting for Ollama... ({attempt + 1}/15)")

    print("Ollama didn't start in 15s — open it manually.")
    return False


if not check_ollama():
    sys.exit(1)
memory = load_memory()

if memory.get("name") is None:
    name = input("FRIDAY: I don't know you yet. What's your name? ")
    memory["name"] = name
    save_memory(memory)
    print(f"FRIDAY: Nice to meet you, {name}!")
else:
    print(f"FRIDAY: Welcome back, {memory['name']}!")

system_prompt = build_system_prompt(memory)
messages = [{"role": "system", "content": system_prompt}]

while True:
    user_input = input("You: ")
    if not user_input.strip():
        continue
    if user_input.lower() =="/help" or user_input.lower()=="help":
        show_help()
        continue
    if user_input.lower() == "exit":
        break

    if user_input.lower() == "time":
        print("FRIDAY:", get_time())
        continue

    if user_input.lower() == "date":
        print("FRIDAY:", get_date())
        continue
    if user_input.lower() == "facts":
        if memory.get("facts"):
            print(format_facts(memory["facts"]))
        else:
            print("FRIDAY: I don't remember any facts yet.")
        continue


    if user_input.lower().startswith("open "):
        app = user_input[len("open "):]
        print("FRIDAY:", open_app(app))
        continue

    if user_input.lower().startswith("search "):
        query = user_input[len("search "):]
        print("FRIDAY:", search_web(query))
        continue

    if user_input.lower().startswith("remember "):
        rest = user_input[9:]
        if "=" not in rest:
            print("Usage: remember category.key = value")
            continue
        key_part, value = rest.split("=", 1)
        key_part = key_part.strip().lower()
        value = value.strip()
        keys = key_part.split(".")
        node = memory["facts"]
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = value
        save_memory(memory)
        print(f"[saved ✓] {key_part} = {value}")
        continue
    if user_input.lower().startswith("forget "):
        key_part = user_input[len("forget "):].strip().lower()
        keys = key_part.split(".")
        node = memory["facts"]
        try:
            for k in keys[:-1]:
                node = node[k]                  
            removed = node.pop(keys[-1])             
            save_memory(memory)
            print(f"[forgotten ✗] {key_part} = {removed}")
        except KeyError:
            print(f"FRIDAY: I don't have anything stored at '{key_part}'.")
        continue


    messages.append({"role": "user", "content": user_input})
    messages = trim(messages, 10)
    try:
        response = chat(
            model=MODEL,
            messages=messages,
            think=False
        )
    except ollama.ResponseError:
        print("FRIDAY: Model error — run 'ollama list' to check it's pulled.")
        messages.pop()
        continue
    except Exception as err:
        print(f"FRIDAY: Can't reach Ollama ({err}).")
        messages.pop()
        continue

    content = response.message.content
    if THINK_TAG in content:
        content = content.split(THINK_TAG, 1)[1]
    print("Friday:", content.strip())
    messages.append({"role": "assistant", "content": content.strip()})
