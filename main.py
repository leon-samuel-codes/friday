from ollama import chat
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
               
def save_memory():
    with open("memory.json", "w") as file:
        json.dump(memory , file, indent=2)  
memory = load_memory()



if memory.get("name") is None:              
    name = input("FRIDAY: I don't know you yet. What's your name? ")
    memory["name"] = name
    save_memory()                           
    print(f"FRIDAY: Nice to meet you, {name}!")
else:
    print(f"FRIDAY: Welcome back, {memory['name']}!")


system_prompt = "You are FRIDAY, a sharp and loyal AI assistant. Keep answers short and direct."

if memory.get("name"):
    system_prompt += f" The user's name is {memory['name']}. Call them by their name sometimes."


if memory.get("facts"):
        facts_sentence = "; ".join(memory["facts"])
        system_prompt += f" Facts about the user: {facts_sentence}"



messages = [{"role": "system", "content": system_prompt}]

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break
    if user_input.lower().startswith("remember "):
        fact=user_input[9:]
        memory["facts"].append(fact)
        save_memory()
        print(f"FRIDAY: Got it! I will remember {fact}")
    messages.append({"role": "user", "content": user_input})  

    response = chat(
        model="qwen3:4b",
        messages=messages
           
    )

    print("Friday:", response.message.content)                     
    messages.append({"role": "assistant", "content": response.message.content})   
