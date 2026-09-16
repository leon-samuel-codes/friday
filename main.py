from ai import build_system_prompt     
from ollama import chat
from memory import load_memory,  save_memory 
from commands import get_time, get_date
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
    if user_input.lower().startswith("remember "):
        fact=user_input[9:]
        memory["facts"].append(fact)
        save_memory(memory)
        print("[saved ✓]")
    messages.append({"role": "user", "content": user_input})  
    response = chat(
        model="qwen3:4b",
        messages=messages,
        think=False    
    )
    content = response.message.content
    if "</think>" in content:
        content = content.split("</think>", 1)[1]
    print("Friday:", content.strip())
    messages.append({"role": "assistant", "content": content.strip()})
        
