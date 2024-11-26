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
from transformers import pipeline
from dotenv import load_dotenv

# Load summarization pipeline (use a small model for speed)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

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
    Perform a web search using Serper API and summarize the results.
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

        # Extract and summarize the results
        if "organic" in data:
            results = data["organic"]
            content_to_summarize = " ".join([result['snippet'] for result in results[:5]])  # Top 5 results
            summary = summarizer(content_to_summarize, max_length=100, min_length=30, do_sample=False)
            summarized_text = summary[0]['summary_text']

            # Format and return results
            top_results = [
                f"{i+1}. {result['title']} - {result['link']}"
                for i, result in enumerate(results[:5])
            ]
            return f"Summary:\n{summarized_text}\n\nCitations:\n" + "\n".join(top_results)
        else:
            return "No search results found."
    except Exception as e:
        return f"An error occurred while performing the web search: {e}"