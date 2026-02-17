from pynput import keyboard, mouse
import threading
import os
try:
    import evdev
    from evdev import InputDevice, ecodes
except ImportError:
    evdev = None

import subprocess
import grp

from controller.path_manager import path_manager

logger = path_manager.get_logger("ActivityTracker")

key_count = 0
click_count = 0
keyboard_listener = None
mouse_listener = None
evdev_threads = []
stopwatch_instance = None  # To store the stopwatch instance

def check_permissions():
    """Check if the user has permissions to read input devices."""
    if os.name != 'posix':
        return True
    
    try:
        input_gid = grp.getgrnam('input').gr_gid
        return input_gid in os.getgroups() or os.getuid() == 0
    except (KeyError, ImportError):
        return False

def request_permission_fix():
    """Attempt to add the user to the input group using pkexec."""
    user = os.getlogin()
    command = f"pkexec usermod -aG input {user}"
    try:
        subprocess.run(command.split(), check=True)
        return True
    except Exception as e:
        logger.error(f"Failed to run permission fix: {e}")
        return False


def on_key_press(key):
    """Handles global key press events for pynput."""
    global key_count
    try:
        if stopwatch_instance and getattr(stopwatch_instance, "running", False):
            key_count += 1
    except Exception as e:
        pass


def on_click(x, y, button, pressed):
    """Handles global mouse click events for pynput."""
    global click_count
    try:
        if pressed and stopwatch_instance and getattr(stopwatch_instance, "running", False):
            click_count += 1
    except Exception as e:
        pass

def evdev_worker(device_path, dev_type):
    """Handles global events for evdev (Wayland)."""
    global key_count, click_count
    try:
        device = InputDevice(device_path)
        for event in device.read_loop():
            if stopwatch_instance and getattr(stopwatch_instance, "running", False):
                if event.type == ecodes.EV_KEY and event.value == 1: # Key down
                    if dev_type == 'kbd':
                        key_count += 1
                    elif dev_type == 'mouse' and event.code in [ecodes.BTN_LEFT, ecodes.BTN_RIGHT, ecodes.BTN_MIDDLE, ecodes.BTN_SIDE, ecodes.BTN_EXTRA]:
                        click_count += 1
    except (PermissionError, Exception) as e:
        logger.error(f"Evdev error on {device_path}: {e}")


def start_tracking(stopwatch):
    """Start global listeners for keyboard and mouse events."""
    global keyboard_listener, mouse_listener, stopwatch_instance, evdev_threads
    stopwatch_instance = stopwatch

    session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
    
    if session_type == 'wayland' and evdev:
        logger.info("Wayland detected. Attempting to use evdev for tracking...")
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        
        # Simple heuristic to identify keyboard and mouse
        # Improving this by looking at capabilities if needed
        for device in devices:
            is_kbd = False
            is_mouse = False
            caps = device.capabilities()
            
            if ecodes.EV_KEY in caps:
                # Keyboards usually have many keys, mice have buttons
                keycodes = caps[ecodes.EV_KEY]
                if ecodes.KEY_A in keycodes:
                    is_kbd = True
                if ecodes.BTN_LEFT in keycodes:
                    is_mouse = True
            
            if is_kbd or is_mouse:
                dev_type = 'kbd' if is_kbd else 'mouse'
                t = threading.Thread(target=evdev_worker, args=(device.path, dev_type), daemon=True)
                t.start()
                evdev_threads.append(t)
                logger.info(f"Started evdev listener for {device.name} ({dev_type})")
        
        if not evdev_threads:
            logger.error("ERROR: NO INPUT DEVICES FOUND VIA EVDEV")
            logger.info("Possible permission issue. Run this to fix:")
            logger.info(f"  sudo usermod -aG input {os.getlogin()}")
            logger.info("Then log out and log back in.")
    else:
        # X11 or fallback
        logger.info("Session is X11 or Wayland without evdev. Using pynput...")
        try:
            keyboard_listener = keyboard.Listener(on_press=on_key_press)
            mouse_listener = mouse.Listener(on_click=on_click)
            keyboard_listener.start()
            mouse_listener.start()
            logger.info("Started pynput listeners")
        except Exception as e:
            logger.error(f"Could not start pynput listeners: {e}")


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

    logger.info("Stopped listening to global events")
