"""Voice — Phase 10.

Optional pieces, each checked before use:
  pyttsx3        - text-to-speech (offline)
  faster-whisper - speech-to-text (offline)
  pynput         - push-to-talk key (no wake word yet)
  sounddevice    - microphone input
FRIDAY works fine without any of them. Turn voice on with /voice.
"""

import time

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

try:
    from pynput import keyboard as pynput_keyboard
except ImportError:
    pynput_keyboard = None

PUSH_TO_TALK = "f19"   # hold this key and speak


class Voice:
    """Speaks replies and listens with push-to-talk.
    Never does both at once (turn-taking)."""

    def __init__(self):
        self.enabled = False
        self.speaking = False     # turn-taking guard
        self._engine = None       # pyttsx3 engine, made on first use
        self._model = None        # faster-whisper model, made on first use

    def say(self, text):
        """Speak text aloud (only when voice is on)."""
        if not self.enabled or not text:
            return
        if pyttsx3 is None:
            print("FRIDAY: voice out needs: pip install pyttsx3")
            return
        if self._engine is None:
            self._engine = pyttsx3.init()
        self.speaking = True
        self._engine.say(text)
        self._engine.runAndWait()
        self.speaking = False

    @staticmethod
    def _open_mic(sd):
        """Open a 16 kHz mono input stream. Tries the default
        device first, then every input device — the Windows
        default input is sometimes broken (MME error 1)."""
        try:
            return sd.InputStream(samplerate=16000, channels=1,
                                  dtype="int16")
        except Exception:
            pass
        for index in range(len(sd.query_devices())):
            info = sd.query_devices(index)
            if info["max_input_channels"] < 1:
                continue
            try:
                return sd.InputStream(samplerate=16000, channels=1,
                                      dtype="int16", device=index)
            except Exception:
                continue
        return None

    def listen(self):
        """Hold the push-to-talk key, speak, release.
        Returns the transcript (or '' if nothing was heard)."""
        if WhisperModel is None or pynput_keyboard is None:
            print("FRIDAY: voice in needs: pip install faster-whisper pynput sounddevice")
            return ""
        if self.speaking:                 # turn-taking: never listen while speaking
            return ""
        import numpy as np
        import sounddevice as sd

        if self._model is None:
            self._model = WhisperModel("small")

        print(f"FRIDAY: hold {PUSH_TO_TALK.upper()} and speak...")
        held = {"down": False}

        def on_press(key):
            if getattr(key, "name", "") == PUSH_TO_TALK:
                held["down"] = True
            return True

        def on_release(key):
            if getattr(key, "name", "") == PUSH_TO_TALK:
                return False              # stop listening on release
            return True

        frames = []
        try:
            with pynput_keyboard.Listener(on_press=on_press,
                                          on_release=on_release) as keys:
                # Wait for the push-to-talk key BEFORE recording.
                # Without this, the loop below checks held["down"]
                # while it's still False and exits instantly, so
                # nothing is ever recorded.
                while not held["down"] and keys.is_alive():
                    time.sleep(0.01)
                mic = self._open_mic(sd)
                if mic is None:
                    print("FRIDAY: Couldn't open any microphone — "
                          "check your Windows sound settings.")
                    return ""
                with mic:
                    while held["down"] and keys.is_alive():
                        frames.append(mic.read(1600)[0])   # 100 ms chunks
        except Exception as err:
            print(f"FRIDAY: Listening failed ({err}).")
            return ""

        if not frames:
            return ""
        audio = np.concatenate(frames).flatten().astype(np.float32) / 32768.0
        try:
            # ndarray input must already be 16 kHz mono — we
            # recorded it that way. (faster-whisper's transcribe()
            # has no samplerate argument.)
            segments, _ = self._model.transcribe(audio)
        except Exception as err:
            print(f"FRIDAY: Couldn't transcribe ({err}).")
            return ""
        return " ".join(seg.text for seg in segments).strip()
