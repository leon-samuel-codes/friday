"""FRIDAY's memory: facts (memory.json) and chat history (history.json).

Phase 11: the Memory class replaces the old load_memory()/save_memory()
functions.
Phase R item 4: paths are anchored to THIS file's folder, so FRIDAY
works no matter which folder you run it from.
"""

import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MEMORY_FILE = str(BASE_DIR / "memory.json")
HISTORY_FILE = str(BASE_DIR / "history.json")
CORRUPT_FILE = str(BASE_DIR / "memory.corrupt.json")


class Memory:
    """Holds the user's name, remembered facts, and the chat history."""

    def __init__(self):
        self.data = self._load_facts()

    def _load_facts(self):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return {"name": None, "facts": {}}
        except json.JSONDecodeError:
            print("⚠️  memory.json is corrupted — rescuing it as memory.corrupt.json")
            try:
                os.replace(MEMORY_FILE, CORRUPT_FILE)
            except OSError:
                pass
            return {"name": None, "facts": {}}
        except OSError as err:
            print(f"⚠️  Couldn't read memory.json ({err}) — starting with empty memory.")
            return {"name": None, "facts": {}}

        if "facts" not in data:
            data["facts"] = {}
        return data

    # -- facts ------------------------------------------------------

    @property
    def name(self):
        return self.data.get("name")

    @property
    def facts(self):
        return self.data.setdefault("facts", {})

    def remember(self, dotted_key, value):
        """Store a fact. 'school.subject' becomes facts -> school -> subject."""
        keys = dotted_key.split(".")
        node = self.facts
        for key in keys[:-1]:
            node = node.setdefault(key, {})
        node[keys[-1]] = value
        self.save()

    def forget(self, dotted_key):
        """Remove a fact (or a whole top-level slot). Raises KeyError if missing."""
        keys = dotted_key.split(".")
        node = self.facts
        for key in keys[:-1]:
            node = node[key]
        return node.pop(keys[-1])

    def save(self):
        """Atomic write: temp file first, then swap. A crash can't
        leave a half-written memory.json."""
        tmp = MEMORY_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=2)
        os.replace(tmp, MEMORY_FILE)

    # -- chat history (Phase S) -------------------------------------

    def load_history(self):
        """The saved conversation (without the system prompt), or [] if none."""
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                history = json.load(file)
            return history if isinstance(history, list) else []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    def save_history(self, messages):
        tmp = HISTORY_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as file:
            json.dump(messages, file, indent=2)
        os.replace(tmp, HISTORY_FILE)
