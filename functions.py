import os
import psutil
import ctypes
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import wmi
import pythoncom
import requests
# from bs4 import BeautifulSoup
# from transformers import pipeline
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def set_brightness(brightness: int) -> str:
    """
    Set the screen brightness on Windows.
    """
    if 0 <= brightness <= 100:
        try:
            # Initialize COM for multi-threaded environments
            pythoncom.CoInitialize()
            
            wmi_interface = wmi.WMI(namespace='root\\WMI')
            methods = wmi_interface.WmiMonitorBrightnessMethods()[0]
            methods.WmiSetBrightness(brightness, 0)  # Second argument is timeout (0 = immediate)
            
            return f"Brightness set to {brightness}%"
        except Exception as e:
            return f"Failed to set brightness: {e}"
        finally:
            # Uninitialize COM
            pythoncom.CoUninitialize()
    else:
        return "Invalid brightness percentage. Please use a value between 0 and 100."
    


def set_volume(volume: int) -> str:
    """
    Set the system volume on Windows.
    """
    if 0 <= volume <= 100:
        try:
            # Initialize COM for multi-threaded environments
            pythoncom.CoInitialize()
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            
            # Convert volume percentage to scalar (0.0 to 1.0)
            volume_interface.SetMasterVolumeLevelScalar(volume / 100, None)
            return f"Volume set to {volume}%"
        except Exception as e:
            return f"Failed to set volume: {e}"
        finally:
            # Uninitialize COM to clean up resources
            pythoncom.CoUninitialize()
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

# def get_storage_info(drive: str) -> str:
#     """
#     Get storage details for the specified drive.
#     """
#     # Ensure the drive ends with a backslash
#     if not drive.endswith("\\"):
#         drive += "\\"
    
#     try:
#         usage = psutil.disk_usage(drive)
#         free_space = usage.free // (1024**3)  # Convert bytes to GB
#         total_space = usage.total // (1024**3)  # Convert bytes to GB
#         return f"Drive {drive} has {free_space} GB free out of {total_space} GB."
#     except FileNotFoundError:
#         return f"Drive {drive} is not available."
#     except Exception as e:
#         return f"An error occurred while accessing drive {drive}: {e}"

def get_storage_info(drive: str) -> str:
    if not drive.endswith("\\") and os.name == "nt":  # For Windows
        drive += "\\"
    usage = psutil.disk_usage(drive)
    return f"Drive {drive} has {usage.free // (1024**3)} GB free out of {usage.total // (1024**3)} GB."


def open_application(app_path: str) -> str:
    """
    Open a specified application.
    """
    try:
        os.startfile(app_path)
        return f"Application at {app_path} opened successfully."
    except Exception as e:
        return f"Failed to open application: {e}"
    
def search_web(query: str) -> str:
    """
    Perform a web search using Serper API.
    """
    try:
        url = "https://google.serper.dev/search"
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": SERPER_API_KEY
        }
        payload = {"q": query}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Debug the response from Serper API
        print(f"Serper API Response: {data}")

        # Extract and return top search results
        if "organic" in data:
            results = data["organic"]
            if not results:
                return "No results found for your query."
            top_results = [
                f"{i+1}. {result['title']} - {result['link']}"
                for i, result in enumerate(results[:5])
            ]
            return "Top Search Results:\n" + "\n".join(top_results)
        else:
            return "No results found for your query."
    except Exception as e:
        return f"Error during web search: {e}"



