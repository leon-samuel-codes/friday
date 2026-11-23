"""FRIDAY — the main program.

This is the complete build: every roadmap phase (1–14),
the review fixes (Phase R), and streaming + chat-history
persistence (Phase S), all in one runnable assistant.

Optional extras (voice, HUD, Telegram) are imported
lazily and degrade gracefully when their packages are
missing — FRIDAY works without any of them.

Run it from this folder:  python main.py
"""

import os
import sys
import time

import ollama
from ollama import chat

import commands
import telegram_remote
from ai import build_system_prompt, trim
from hud import HUD
from memory import Memory
from modes import ModeManager
from router import CommandRouter
from voice import Voice

MODEL = "qwen3:4b-instruct"
THINK_TAG = "</think>"


def check_ollama():
    """Make sure Ollama is up before anything else (Phase H)."""
    try:
        ollama.list()
        return True
    except Exception:
        pass

    print("FRIDAY: Ollama isn't running — starting it...")
    local_app_data = os.environ.get("LOCALAPPDATA")      # Phase R item 5
    if not local_app_data:
        print("Couldn't find the Ollama folder — start it manually.")
        return False
    ollama_path = os.path.join(local_app_data, "Programs",
                               "Ollama", "Ollama.exe")
    try:
        os.startfile(ollama_path)
    except (OSError, AttributeError):
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


def stream_chat(messages, echo=None):
    """Ask the model and print the reply as it streams out (Phase S).

    Returns the full reply, or None when the call failed —
    the caller then pops its user message (Phase H).
    """
    if echo is None:
        def echo(text):
            print(text, end="", flush=True)
    try:
        stream = chat(model=MODEL, messages=messages,
                      stream=True, think=False)
        parts = []
        echo("FRIDAY: ")
        for chunk in stream:
            piece = chunk.message.content or ""
            if piece:
                echo(piece)
                parts.append(piece)
        echo("\n")
        return "".join(parts)
    except ollama.ResponseError:
        echo("FRIDAY: Model error — run 'ollama list' to check "
             "it's pulled.\n")
    except Exception as err:
        echo(f"FRIDAY: Can't reach Ollama ({err}).\n")
    return None


def main():
    if not check_ollama():
        sys.exit(1)

    memory = Memory()
    if memory.name is None:
        name = input("FRIDAY: I don't know you yet. "
                     "What's your name? ").strip()
        memory.data["name"] = name
        memory.save()
        print(f"FRIDAY: Nice to meet you, {name}!")
    else:
        print(f"FRIDAY: Welcome back, {memory.name}!")

    voice = Voice()
    mode_manager = ModeManager()
    hud_display = HUD()

    messages = [{"role": "system",
                 "content": build_system_prompt(memory)}]
    messages.extend(memory.load_history())          # Phase S: restore
    messages[:] = trim(messages, 10)

    def refresh_prompt():                            # Phase R item 1
        messages[0]["content"] = build_system_prompt(memory)

    def new_conversation():                          # Phase S: /new
        messages[:] = messages[:1]
        memory.save_history([])

    router = CommandRouter(memory, mode_manager=mode_manager,
                           on_memory_change=refresh_prompt,
                           on_new=new_conversation)

    print("FRIDAY: Ask me anything — or type 'help'.")

    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nFRIDAY: Bye!")
            break

        if not user_input.strip():
            continue
        low = user_input.lower()

        # -- front-end switches (they need live objects) --
        if low == "exit":
            print("FRIDAY: Bye!")
            break
        if low in ("/voice", "voice"):
            voice.enabled = not voice.enabled
            print("FRIDAY: Voice replies",
                  "on." if voice.enabled else "off.")
            continue
        if low == "/listen":
            heard = voice.listen()
            if heard:
                print("You (voice):", heard)
                user_input, low = heard, heard.lower()
            else:
                print("FRIDAY: Didn't catch that.")
                continue
        if low == "/telegram":
            print("FRIDAY:", telegram_remote.run(memory, router,
                                                  stream_chat))
            continue
        if low == "/hud":
            hud_display.toggle()
            continue

        # -- shared command router (Phases 9/11/13) --
        reply = router.process_command(user_input)
        if reply is not None:
            print("FRIDAY:", reply)
            voice.say(reply)
            hud_display.set_mode(mode_manager.current)
            hud_display.set_action(reply[:80])
            continue

        # -- live web answers (Phase 7) --
        if low.startswith("ask "):
            question = user_input[4:].strip()
            results = commands.ask(question)
            content = (f"Live search results for '{question}':\n"
                       + results
                       + f"\n\nUsing only these results, answer: {question}")
            messages.append({"role": "user", "content": content})
            messages[:] = trim(messages, 10)
            answer = stream_chat(messages)
            if answer is None:
                messages.pop()
                continue
            voice.say(answer)
            messages.append({"role": "assistant",
                             "content": answer.strip()})
            memory.save_history(messages[1:])
            hud_display.set_action(answer[:80])
            continue

        # -- chat with the model --
        messages.append({"role": "user", "content": user_input})
        messages[:] = trim(messages, 10)
        reply = stream_chat(messages)
        if reply is None:
            messages.pop()                           # Phase H
            continue
        if THINK_TAG in reply:                       # Phase R item 6
            tail = reply.split(THINK_TAG, 1)[1]
            if tail.strip():                         # only strip a real
                reply = tail                         # remainder
        reply = reply.strip()
        voice.say(reply)
        messages.append({"role": "assistant", "content": reply})
        memory.save_history(messages[1:])            # Phase S: persist
        hud_display.set_action(reply[:80])


if __name__ == "__main__":
    main()
