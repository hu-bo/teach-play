import json
import time
from pathlib import Path
from PIL import ImageGrab
from pynput import mouse, keyboard

OUT_DIR = Path(__file__).parents[3] / 'data' / 'recordings'
OUT_DIR.mkdir(parents=True, exist_ok=True)


class Recorder:
    def __init__(self):
        self.events = []
        self.start_time = None

    def _capture_frame_text(self, x, y):
        # placeholder: capture small region for OCR later
        bbox = (x - 100, y - 20, x + 100, y + 20)
        img = ImageGrab.grab(bbox)
        return None

    def _on_click(self, x, y, button, pressed):
        if not pressed:
            return
        if self.start_time is None:
            self.start_time = time.time()
        evt = {
            'type': 'click',
            'timestamp': time.time(),
            'position': {'x': int(x), 'y': int(y)},
            'button': str(button),
            'mode': 'absolute_position',
            'context': {}
        }
        self.events.append(evt)

    def _on_scroll(self, x, y, dx, dy):
        if self.start_time is None:
            self.start_time = time.time()
        evt = {
            'type': 'scroll',
            'timestamp': time.time(),
            'position': {'x': int(x), 'y': int(y)},
            'delta': int(dy),
            'mode': 'absolute_position',
            'context': {}
        }
        self.events.append(evt)

    def _on_press(self, key):
        if self.start_time is None:
            self.start_time = time.time()
        try:
            k = key.char
        except AttributeError:
            k = str(key)
        evt = {
            'type': 'key',
            'timestamp': time.time(),
            'key': k,
            'mode': 'keyboard',
            'context': {}
        }
        self.events.append(evt)

    def record(self, duration=None):
        mouse_listener = mouse.Listener(on_click=self._on_click, on_scroll=self._on_scroll)
        kb_listener = keyboard.Listener(on_press=self._on_press)
        mouse_listener.start()
        kb_listener.start()
        try:
            if duration:
                time.sleep(duration)
            else:
                print('Recording... Press Ctrl+C to stop')
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            pass
        mouse_listener.stop()
        kb_listener.stop()
        return self._save()

    def _save(self):
        ts = int(time.time())
        out = OUT_DIR / f'recording_{ts}.json'
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)
        print('Saved recording to', out)
        return out


def main():
    r = Recorder()
    r.record()


if __name__ == '__main__':
    main()
