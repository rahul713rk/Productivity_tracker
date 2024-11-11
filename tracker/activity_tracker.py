from pynput import keyboard, mouse
import threading

key_count = 0
click_count = 0
keyboard_listener = None 
mouse_listener = None

def on_key_press(key):
    global key_count
    key_count += 1

def on_click(x, y, button, pressed):
    global click_count
    if pressed:
        # print(x , y)
        # print("Mouse Button : " , button)
        click_count += 1

def start_tracking(stopwatch):
    global keyboard_listener , mouse_listener
    print("Started Listening events")
    keyboard_listener = keyboard.Listener(
        on_press=lambda key: on_key_press(key) if stopwatch.running else None
    )
    mouse_listener = mouse.Listener(
        on_click=lambda x, y, button, pressed: on_click(x, y, button, pressed) if stopwatch.running else None
    )

    keyboard_thread = threading.Thread(target=keyboard_listener.start , daemon=True)
    mouse_thread = threading.Thread(target=mouse_listener.start, daemon=True)

    keyboard_thread.start()
    mouse_thread.start()

def get_count():
    return key_count , click_count

def stop_tracking():
        """Stop the tracking listeners."""
        if keyboard_listener:
            keyboard_listener.stop()
        if mouse_listener:
            mouse_listener.stop()
        print("Stopped listening events")