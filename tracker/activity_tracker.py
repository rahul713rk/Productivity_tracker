from pynput import keyboard, mouse

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

    keyboard_listener.start()
    mouse_listener.start()
