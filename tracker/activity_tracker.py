from pynput import keyboard, mouse
import threading

key_count = 0
click_count = 0
keyboard_listener = None
mouse_listener = None
stopwatch_instance = None  # To store the stopwatch instance


def on_key_press(key):
    """Handles global key press events."""
    global key_count
    if stopwatch_instance and getattr(stopwatch_instance, "running", False):
        key_count += 1


def on_click(x, y, button, pressed):
    """Handles global mouse click events."""
    global click_count
    if pressed and stopwatch_instance and getattr(stopwatch_instance, "running", False):
        click_count += 1


def start_tracking(stopwatch):
    """Start global listeners for keyboard and mouse events."""
    global keyboard_listener, mouse_listener, stopwatch_instance
    stopwatch_instance = stopwatch  # Store the reference to the stopwatch

    print("Started Listening to global events")

    # Initialize the listeners
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    mouse_listener = mouse.Listener(on_click=on_click)

    # Start listeners
    keyboard_listener.start()
    mouse_listener.start()


def get_count():
    """Returns the counts for key presses and mouse clicks."""
    return key_count, click_count


def stop_tracking():
    """Stops the global listeners."""
    global keyboard_listener, mouse_listener, stopwatch_instance
    stopwatch_instance = None  # Clear the stopwatch reference

    if keyboard_listener:
        keyboard_listener.stop()
        keyboard_listener = None

    if mouse_listener:
        mouse_listener.stop()
        mouse_listener = None

    print("Stopped listening to global events")
