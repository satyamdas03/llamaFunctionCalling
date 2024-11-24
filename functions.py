import os
import psutil

def set_brightness(brightness: int) -> str:
    """
    Set the screen brightness (if supported by the system).
    """
    if 0 <= brightness <= 100:
        os.system(f"xrandr --output eDP-1 --brightness {brightness / 100}")
        return f"Brightness set to {brightness}%"
    else:
        return "Invalid brightness percentage. Please use a value between 0 and 100."

def set_volume(volume: int) -> str:
    """
    Set the system volume.
    """
    if 0 <= volume <= 100:
        os.system(f"amixer set Master {volume}%")
        return f"Volume set to {volume}%"
    else:
        return "Invalid volume percentage. Please use a value between 0 and 100."

def get_battery() -> str:
    """
    Get the current battery percentage.
    """
    battery = psutil.sensors_battery()
    if battery:
        return f"Battery is at {battery.percent}%"
    return "Battery information not available."
