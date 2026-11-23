"""HUD overlay — Phase 14 (PyQt5).

A small always-on-top window showing the active mode and
the current action — the Iron Man HUD effect.

Optional: without PyQt5, FRIDAY just skips the HUD. The
HUD runs in its own thread; updates arrive through a
queue, so the terminal loop never blocks on Qt.
"""

import queue
import threading

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (QApplication, QLabel, QVBoxLayout,
                                 QWidget)
    PYQT5 = True
except ImportError:
    PYQT5 = False


class HUD:
    """Floating status overlay. toggle() it on, then
    call set_mode() / set_action() from anywhere."""

    def __init__(self):
        self.enabled = False
        self._app = None
        self._window = None
        self._mode_label = None
        self._action_label = None
        self._updates = queue.Queue()
        self._thread = None

    def toggle(self):
        if not PYQT5:
            print("FRIDAY: HUD needs PyQt5 — run: pip install PyQt5")
            return
        self.enabled = not self.enabled
        if self.enabled and (self._thread is None
                             or not self._thread.is_alive()):
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def set_mode(self, mode):
        if self.enabled:
            self._updates.put(("mode", mode or "—"))

    def set_action(self, action):
        if self.enabled:
            self._updates.put(("action", action or "—"))

    def _run(self):
        # Everything Qt — including the teardown — happens in
        # THIS thread. Destroying a QApplication from the wrong
        # thread makes Python segfault when it exits.
        try:
            self._app = QApplication([])
            self._window = QWidget()
            self._window.setWindowFlags(Qt.FramelessWindowHint
                                        | Qt.WindowStaysOnTopHint | Qt.Tool)
            self._window.setAttribute(Qt.WA_TranslucentBackground)
            self._window.setFixedSize(340, 150)
            self._window.move(30, 30)
            layout = QVBoxLayout(self._window)
            self._mode_label = QLabel("MODE  —")
            self._action_label = QLabel("ACTION  —")
            for label in (self._mode_label, self._action_label):
                label.setStyleSheet("color: #7fd4ff; font: bold 15px;"
                                    "background: transparent;")
                layout.addWidget(label)
            self._window.show()

            # Drain the update queue; Qt only draws inside this
            # thread, where its QApplication lives.
            while self.enabled:
                self._app.processEvents()
                try:
                    kind, text = self._updates.get(timeout=0.1)
                except queue.Empty:
                    continue
                if kind == "mode":
                    self._mode_label.setText("MODE  " + text)
                else:
                    self._action_label.setText("ACTION  " + text)
        finally:
            if self._window is not None:
                self._window.close()
                self._window.deleteLater()
                self._app.processEvents()
                self._window = None
                self._mode_label = None
                self._action_label = None
            if self._app is not None:
                self._app.quit()
                self._app = None      # destroyed in THIS thread
