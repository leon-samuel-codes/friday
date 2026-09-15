
from ai import build_system_prompt     
from ollama import chat

from memory import load_memory,  save_memory 

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
    if user_input.lower().startswith("remember "):
        fact=user_input[9:]
        memory["facts"].append(fact)
        save_memory(memory)
        print("[saved ✓]")

    messages.append({"role": "user", "content": user_input})  

    response = chat(
        model="qwen3:4b",
        messages=messages
           
    )

    print("Friday:", response.message.content)                     
    messages.append({"role": "assistant", "content": response.message.content})   
