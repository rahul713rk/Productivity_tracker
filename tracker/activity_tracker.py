from pynput import keyboard, mouse
import threading

# Global counters
key_count = 0
click_count = 0

def on_key_press(key):
    global key_count
    key_count += 1

def on_click(x, y, button, pressed):
    global click_count
    if pressed:
        click_count += 1

def start_tracking(stopwatch):
    keyboard_listener = keyboard.Listener(
        on_press=lambda key: on_key_press(key) if stopwatch.running else None
    )
    mouse_listener = mouse.Listener(
        on_click=lambda x, y, button, pressed: on_click(x, y, button, pressed) if stopwatch.running else None
    )

    # Start listeners in separate threads
    keyboard_thread = threading.Thread(target=keyboard_listener.start)
    mouse_thread = threading.Thread(target=mouse_listener.start)

    keyboard_thread.start()
    mouse_thread.start()

    # Join threads to ensure listeners continue even when minimized
    keyboard_thread.join()
    mouse_thread.join()
