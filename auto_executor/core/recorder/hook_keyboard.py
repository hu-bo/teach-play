# Stub for cross-platform keyboard hook utilities
from pynput import keyboard

def start_keyboard_listener(on_press=None):
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    return listener
