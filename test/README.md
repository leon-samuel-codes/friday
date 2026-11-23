# FRIDAY — complete build (test folder)

Every roadmap phase (1–14), plus the Phase R review
fixes and Phase S (streaming + chat history), as a
standalone copy of FRIDAY. The root-level files are
untouched.

## Run it

    python main.py

## Files

| File | What it is |
|---|---|
| main.py | Entry point: startup check, chat loop, streaming (Phase S) |
| memory.py | Memory class — facts + chat history (Phases 1, 11, S) |
| ai.py | System prompt, trimming, fact formatting (Phases Q, R) |
| commands.py | Rule-based commands, APIs, system tools (Phases 3, 4, 7, 8, 12) |
| router.py | CommandRouter — match-case routing (Phases 9, 11, 13) |
| modes.py | ModeManager — action modes that close/open apps (Phase 12) |
| voice.py | Voice in/out with push-to-talk (Phase 10) |
| contacts.py | Contact Book — Phase 11 practice mini-boss |
| telegram_remote.py | Telegram remote control (Phase 13) |
| hud.py | PyQt5 HUD overlay (Phase 14) |

## Optional extras (each one is skipped if missing)

- requests — GitHub / dictionary lookups
- duckduckgo_search — `ask <question>` live answers
- psutil — `system`, `killport`, action-mode app closing
- keyboard — `media play / next / prev`
- pyttsx3 — spoken replies (`/voice`)
- faster-whisper, pynput, sounddevice — push-to-talk (`/listen`)
- python-telegram-bot — `/telegram` (set FRIDAY_TELEGRAM_TOKEN
  and FRIDAY_TELEGRAM_USER_ID first)
- PyQt5 — `/hud`

Ollama must be running with qwen3:4b-instruct for chatting.
