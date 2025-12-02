import json
import time
from pathlib import Path
import pyautogui


class Executor:
    def __init__(self):
        pyautogui.FAILSAFE = True

    def load(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            self.actions = json.load(f)

    def run(self):
        if not hasattr(self, 'actions'):
            raise RuntimeError('No actions loaded')
        last_ts = None
        for act in self.actions:
            ts = act.get('timestamp')
            if last_ts is None:
                last_ts = ts
            else:
                delay = ts - last_ts
                if delay > 0:
                    time.sleep(delay)
                last_ts = ts
            if act['type'] == 'click':
                pos = act.get('position')
                if pos:
                    pyautogui.click(pos['x'], pos['y'])
            elif act['type'] == 'scroll':
                pyautogui.scroll(act.get('delta', 0))
            elif act['type'] == 'key':
                k = act.get('key')
                try:
                    pyautogui.press(k)
                except Exception:
                    pyautogui.typewrite(str(k))


def main(path):
    e = Executor()
    e.load(path)
    e.run()
