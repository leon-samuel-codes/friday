# FRIDAY

A local AI assistant built with Python and Ollama — runs entirely on my own PC.

## Features
- Chat powered by a local LLM (Qwen 3 4B via Ollama) — no cloud, no API keys
- Persistent memory (memory.json): remembers my name and facts between sessions
- "remember <fact>" command to store facts about me
- Facts injected into the system prompt so FRIDAY recalls them after restart

## Requirements
- [Ollama](https://ollama.com) with the qwen3:4b model
- Python 3.x with the `ollama` package (`pip install ollama`)

## Run it
ollama run qwen3:4b   (in a separate terminal, first time)
python main.py
