"""Command routing.

Phase 9: the old if/elif chain is now a match-case.
Phase 11: it lives inside the CommandRouter class.
Phase 13: process_command() is the one entry point shared by
the terminal, the Telegram remote, and anything else that
wants to drive FRIDAY.

Routing decision (the roadmap's open question): match-case
inside the CommandRouter class. Tool-calling stays deferred —
the roadmap says it needs its own spec, and choosing it now
would make this and the registry idea moot.
"""

from ai import format_facts
import commands
from modes import ModeManager


class CommandRouter:
    """Turns user text into a reply string.

    Returns None when the text isn't a command — that means
    'send it to the model as chat'.
    """

    def __init__(self, memory, mode_manager=None, on_memory_change=None,
                 on_new=None):
        self.memory = memory
        self.mode_manager = mode_manager or ModeManager()
        # Called after remember/forget so the live system prompt
        # stays fresh (Phase R item 1).
        self.on_memory_change = on_memory_change
        # Called by /new to clear the chat history (Phase S).
        self.on_new = on_new

    def process_command(self, text):
        """The shared command entry point."""
        text = text.strip()
        if not text:
            return ""
        low = text.lower()

        match low:
            case "help" | "/help":
                return commands.show_help()
            case "time":
                return commands.get_time()
            case "date":
                return commands.get_date()
            case "facts":
                if self.memory.facts:
                    return format_facts(self.memory.facts)
                return "I don't remember any facts yet."
            case "system":
                return commands.system_stats()
            case "/new":
                if self.on_new:
                    self.on_new()
                return "Fresh conversation — chat history cleared."
            case "server":
                return self._server("")
            case other if other.startswith("server "):
                return self._server(other[7:].strip())
            case other if other.startswith("killport "):
                return commands.kill_port(other[9:].strip())
            case other if other.startswith("media "):
                return commands.media_key(other[6:].strip())
            case other if other.startswith("open "):
                return commands.open_app(other[5:].strip())
            case other if other.startswith("search "):
                return commands.search_web(other[7:].strip())
            case other if other.startswith("github "):
                return commands.github_lookup(other[7:].strip())
            case other if other.startswith("define "):
                return commands.define(other[7:].strip())
            case other if other.startswith("remember "):
                return self._remember(other[9:])
            case other if other.startswith("forget "):
                return self._forget(other[7:])
            case "mode":
                return self._mode("")
            case other if other.startswith("mode "):
                return self._mode(other[5:].strip())
            case _:
                return None

    # -- commands that touch memory --------------------------------

    def _remember(self, rest):
        if "=" not in rest:
            return "Usage: remember category.key = value"
        key_part, value = rest.split("=", 1)
        key_part = key_part.strip().lower()
        value = value.strip()
        self.memory.remember(key_part, value)
        if self.on_memory_change:
            self.on_memory_change()       # Phase R item 1
        return f"[saved ✓] {key_part} = {value}"

    def _forget(self, key_part):
        key_part = key_part.strip().lower()
        try:
            removed = self.memory.forget(key_part)
        except (KeyError, TypeError):
            return f"I don't have anything stored at '{key_part}'."
        if self.on_memory_change:
            self.on_memory_change()       # Phase R item 1
        return f"[forgotten ✗] {key_part} = {removed}"

    # -- Phase 12: action modes ------------------------------------

    def _mode(self, name):
        if not name:
            return f"Known modes: {self.mode_manager.list_modes()}"
        if name.endswith(" yes"):         # confirmation reply
            return self.mode_manager.activate(name[:-4].strip(), confirm=False)
        return self.mode_manager.activate(name)

    # -- Phase 8: your own server, by saved PID ----------------

    def _server(self, rest):
        if rest.startswith("start "):
            return commands.server_start(rest[6:].strip())
        if rest == "stop":
            return commands.server_stop()
        return "Usage: server start <command> | server stop"
