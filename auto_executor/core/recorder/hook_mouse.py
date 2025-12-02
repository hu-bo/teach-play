# Stub for cross-platform mouse hook utilities
from pynput import mouse

def start_mouse_listener(on_click=None, on_scroll=None):
    listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    listener.start()
    return listener
