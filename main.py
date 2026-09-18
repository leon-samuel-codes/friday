from ai import build_system_prompt, trim
from ollama import chat
from memory import load_memory, save_memory
from commands import get_time, get_date, open_app, search_web
THINK_TAG = "<" + "/" + "think" + ">"


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

    if user_input.lower() == "exit":
        break

    if user_input.lower() == "time":
        print("FRIDAY:", get_time())
        continue

    if user_input.lower() == "date":
        print("FRIDAY:", get_date())
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

    messages.append({"role": "user", "content": user_input})
    messages = trim(messages, 10)

    response = chat(
        model="qwen3:4b",
        messages=messages,
        think=False
    )
    content = response.message.content
    if THINK_TAG in content:
        content = content.split(THINK_TAG, 1)[1]
    print("Friday:", content.strip())
    messages.append({"role": "assistant", "content": content.strip()})
