"""Action modes — Phase 12.

A mode closes a list of apps and opens a list of apps, from
config. This is different from the dropped Soft Mode: that
swapped FRIDAY's personality, this controls running programs.
"""

import os
import sys
import webbrowser

try:
    import psutil
except ImportError:
    psutil = None

# Hardcode your own exact process names and paths — exact names
# matter for psutil matching, and closing the wrong app can
# lose unsaved work.
MODES = {
    "gaming": {
        "close": [],        # e.g. ["code.exe", "discord.exe"]
        "open": [],         # e.g. [r"C:\Program Files (x86)\Steam\steam.exe"]
    },
    "study": {
        "close": [],        # e.g. ["steam.exe"]
        "open": [],
    },
}


class ModeManager:
    """Config-driven mode switcher: a close list + open list per mode."""

    def __init__(self, modes=None):
        self.modes = modes or MODES
        self.current = None        # last activated mode (for the HUD)

    def list_modes(self):
        return ", ".join(sorted(self.modes)) if self.modes else "none"

    def activate(self, name, confirm=True):
        if name not in self.modes:
            return f"Unknown mode '{name}'. Known modes: {self.list_modes()}"
        spec = self.modes[name]

        # Closing apps can lose unsaved work — always confirm first.
        if spec["close"] and confirm:
            return (f"Mode '{name}' will close: {', '.join(spec['close'])}. "
                    f"Say 'mode {name} yes' to confirm.")

        self.current = name          # the HUD shows the active mode
        closed = [self._close_process(p) for p in spec["close"]]
        opened = [self._open_target(t) for t in spec["open"]]

        report = [f"Mode '{name}' on."]
        if closed:
            report.append("Closed: " + ", ".join(closed))
        if opened:
            report.append("Opened: " + ", ".join(opened))
        return " ".join(report)

    def _close_process(self, name):
        if psutil is None:
            return f"{name} (needs psutil)"
        if sys.platform != "win32":
            return f"{name} (Windows only)"
        killed = 0
        for proc in psutil.process_iter(["name"]):
            if proc.info["name"] and proc.info["name"].lower() == name.lower():
                try:
                    proc.terminate()
                    killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                    pass
        return f"{name} ×{killed}" if killed else f"{name} (not running)"

    def _open_target(self, target):
        try:
            if target.startswith("http"):
                webbrowser.open(target)
            elif sys.platform == "win32":
                os.startfile(target)
            else:
                return f"{target} (can't open paths on this OS)"
            return target
        except OSError as err:
            return f"{target} (failed: {err})"
