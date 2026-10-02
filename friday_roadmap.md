# FRIDAY Project Roadmap (Master, Locked)

## Current Status: Phases 1–6 ✅ Complete

| Phase | What it added |
|---|---|
| 1 | Persistent memory — name + facts, saved to `memory.json` |
| 2 | Module split — `main.py` / `memory.py` / `ai.py` / `commands.py` |
| 3 | Rule-based time/date commands (`get_time()`, `get_date()`) |
| 4 | Open apps & web search — `webbrowser`, `os.startfile`, `APPS` dict |
| 5 | Conversation trimming — `trim()` caps message history sent to the model |
| 6 | Structured facts — `remember category.key = value` instead of raw sentences |

Repo: on GitHub, module structure `main / memory / ai / commands`.

**Resolved from the original bug list** (mid-session memory not updating,
missing `continue` after remember, no chat error handling, unbounded
history, duplicate facts) — all fixed by Phases 1, 5 and 6, or made moot by
the key-value fact model. No longer tracked as open issues.

---

## 🧊 Freeze in effect until 8 Oct (exams)
No new FRIDAY work until exams are done. See `roadmap_sept2026_may2027.md`
for the current calendar — that file is the source of truth for dates,
this one just tracks project phases.

---

## Timing: Exams first, hardening in two batches

### Pre-freeze (optional, ~30 min — reuses code you just wrote)
- [ ] **`forget <key.path>`** — reuse the same key-walking loop as `remember`,
  inverted: walk `keys[:-1]` to find the node, then `del node[keys[-1]]`.
  `forget school` deletes a whole top-level slot the same way.
- [ ] **`facts` command** — you already have `format_facts()`; just call
  `print(format_facts(memory["facts"]))`. No numbering needed — it's a
  nested dict, not a flat list.
- [ ] **`/help` command** — list all current commands (time, date, open,
  search, remember, forget, facts)
- [ ] **Prompt wording fix** — tell the model to trust the user's latest
  message over a stored fact if they contradict; wrap the facts block in a
  clear `<user_facts>` tag in `build_system_prompt()`
- [ ] **Date-in-prompt line** — add today's date to the system prompt so
  FRIDAY has date context without a separate command call

### Post-exams (the real hardening pass)
- [ ] **Atomic memory writes** — write to a temp file, then `os.replace()` it
  over `memory.json`. Learn `os.replace` properly when you get here — don't
  paste a generated version's approach without understanding it.
- [ ] **Corrupted-file recovery** — catch `JSONDecodeError` on load, rename
  the broken file to `.corrupt.json`, start fresh instead of crashing
- [✅] **`check_ollama()` startup check** — write your own simple version:
  `try: client.list() / except: print a friendly message and exit`. Keep it
  simple — don't reach for syntax (e.g. `getattr` chains) you haven't learned.
- [ ] **Per-turn error handling around `chat()`** — if a call fails, pop the
  user message you just appended so a failed exchange doesn't pollute history

### Then: Soft Mode (personality mode) — first thing after hardening
The action-mode system in Phase 12 (`ModeManager`, closing apps, launching
Steam) is separate from this. Soft mode is a **personality swap** — a
`PROMPTS` dict keyed by mode name, a `mode <name>` command that swaps which
system prompt is active, and a "game mode" prompt as the first one built (the
10-minute post-exams warm-up). All known concepts: one `.get()` with a
fallback, one command block in the same pattern as your other commands.

---

## Phase 7 — Real data (requests + APIs)
- Watch Bro Code #65 first
- Add a weather command using `requests` + a free weather API
- Handle a failed request / bad API key gracefully

## Phase 8 — System tools
- `subprocess` to start/stop your own hosted server by saved PID
- Find and kill a process by port using `psutil` if you don't control the
  startup script

## Phase 9 — Match-case command router
- Watch Bro Code #38 first
- Replace the growing if/elif chain in `main.py` with `match-case`

## Phase 10 — Voice
- Watch Bro Code #64 (threading) first
- Speech-to-text: `speech_recognition` or `Vosk` (offline)
- Text-to-speech: `pyttsx3` (offline) or a cloud TTS API
- Handle turn-taking: don't listen while it's speaking

## Phase 11 — OOP refactor
- Watch Bro Code #46–57 (OOP block) first
- Refactor into classes: `Memory` class, `CommandRouter` class
- Mini-boss first: build a small Contact Book (`Contact` class, add/search/
  delete) to get comfortable with `self` before refactoring FRIDAY itself

## Phase 12 — Modes & PC control (action modes)
- `ModeManager` class: config-driven `close` list + `open` list per mode
  (e.g. "gaming mode" closes work apps, launches Steam) — distinct from
  Soft Mode above, which swaps personality/prompt, not running apps
- `psutil` to terminate processes by name
- Media-key song control via the `keyboard` module
- Stop/start your own hosted website by saved PID or by port
- Add a confirmation step before closing multiple apps — killing a process
  with unsaved work can lose data
- Hardcode your own app paths/process names rather than letting the LLM
  guess them — exact names matter for `psutil` matching

## Phase 13 — Remote control (Telegram)
- Extract all command handling into one `process_command(text) -> str`
  function shared between the terminal loop and Telegram
- Create a bot via @BotFather, install `python-telegram-bot`
- **Restrict the bot to your own Telegram user ID** — non-negotiable before
  running this outside your own laptop
- Wire incoming messages into `process_command()`

## Phase 14 — PyQt5 GUI/HUD (final)
- Watch Bro Code #66–77 first
- Visual layer showing active mode / current action — the Iron Man HUD effect

---

## Feature Backlog (not yet phased in — pull into a phase when relevant)

### Study companion features *(highest-value — recommended focus once phased in)*
- Pomodoro/study timer: "start a 45 minute study session" — mutes
  notifications, starts a timer, alerts at the end
- Voice-triggered flashcard quiz from a Q&A text file you maintain
- Auto "study mode": close distracting apps, open notes/PDFs, dim
  entertainment app notifications
- Exam countdown: "how many days to my Chemistry unit test?" from a dates file

### System awareness
- Battery %, RAM/CPU usage, disk space on request
- Volume and brightness control by voice
- Clipboard read-back
- Screenshot on command, saved with a timestamp

### Everyday utility commands
- Quick timers/alarms not tied to study
- Simple note-taking: "note this" appends to a timestamped notes file
- Web search shortcut by voice
- Weather check via a free API (overlaps Phase 7)

### Polish & trust
- Confirmation step before destructive actions (overlaps Phase 12)
- Simple tkinter/PyQt5 HUD overlay showing active mode / current action
  (overlaps Phase 14)
- Log file of commands/actions taken
- "Quiet hours" setting so it doesn't interrupt real study blocks

---

## Bro Code Viewing Order (remaining, tied to phases above)
- NOW / whenever convenient: #41 `if __name__ == '__main__'` (not yet
  watched); #13 string methods, #14 slicing (already used in practice — just
  confirm)
- Before Phase 9 (command routing): #38 match-case
- Before Phase 11 (OOP): #46–57 OOP block
- Before Phase 7: #65 requests/APIs
- Before Phase 10: #64 multithreading
- Before Phase 14: #66–77 PyQt5
- Small remaining fundamentals gaps, whenever: #12 conditional expressions,
  #15 format specifiers, #20 nested loops, #32–34 args/kwargs, #35 iterables,
  #36 membership operators, #37 list comprehensions
- Skip: game exercises (5, 17, 19, 24, 28–30, 42–45), #9/#10 conversions
  (your calculator already covers this ground)

---

*Master roadmap, consolidated Sept 2026. Progress: Phases 1–6 complete.
Freeze in effect until 8 Oct — see `roadmap_sept2026_may2027.md` for dates.*
