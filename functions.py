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
import subprocess
import pyttsx3
import win32serviceutil
from PIL import ImageGrab
import pytesseract
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
import time
from voice import speak_response


# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

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
    
def toggle_wifi(state: str) -> str:
    """
    Turn Wi-Fi on or off.
    """
    try:
        if os.name == "nt":  # Windows
            # Get the correct Wi-Fi interface name
            interfaces = subprocess.check_output("netsh interface show interface", shell=True).decode()
            for line in interfaces.splitlines():
                if "Wi-Fi" in line or "Wireless" in line:
                    interface_name = line.split()[-1]  # Extract interface name
                    break
            else:
                return "No Wi-Fi interface found."

            if state.lower() == "on":
                subprocess.run(f"netsh interface set interface \"{interface_name}\" enabled", shell=True, check=True)
                return "Wi-Fi has been turned on."
            elif state.lower() == "off":
                subprocess.run(f"netsh interface set interface \"{interface_name}\" disabled", shell=True, check=True)
                return "Wi-Fi has been turned off."
            else:
                return "Invalid state. Use 'on' or 'off'."
        else:
            return "Wi-Fi control is supported only on Windows."
    except subprocess.CalledProcessError as e:
        return f"Failed to change Wi-Fi state: {e}"



def show_connected_wifi() -> str:
    """
    Show details of the connected Wi-Fi network.
    """
    try:
        if os.name == "nt":  # Windows
            result = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
            return result
        else:
            return "Wi-Fi details are supported only on Windows."
    except subprocess.CalledProcessError as e:
        return f"Failed to retrieve Wi-Fi details: {e}"


def toggle_bluetooth(state: str) -> str:
    """
    Enable or disable Bluetooth by starting or stopping the Bluetooth Support Service.
    """
    try:
        import win32serviceutil
        service_name = "bthserv"

        # Get the current state of the Bluetooth service
        current_state = win32serviceutil.QueryServiceStatus(service_name)[1]

        if state.lower() == "on":
            if current_state == 4:  # 4 = Running
                return "Bluetooth is already turned on."
            win32serviceutil.StartService(service_name)
            return "Bluetooth turned on successfully."
        elif state.lower() == "off":
            if current_state == 1:  # 1 = Stopped
                return "Bluetooth is already turned off."
            win32serviceutil.StopService(service_name)
            return "Bluetooth turned off successfully."
        else:
            return "Invalid Bluetooth state. Use 'on' or 'off'."
    except Exception as e:
        return f"Failed to change Bluetooth state: {e}"



def list_paired_bluetooth_devices() -> str:
    """
    List all paired Bluetooth devices.
    """
    try:
        if os.name == "nt":  # Windows
            result = subprocess.check_output("powershell -Command \"Get-PnpDevice -Class Bluetooth\"", shell=True).decode()
            return result
        else:
            return "Paired Bluetooth devices can only be listed on Windows."
    except subprocess.CalledProcessError as e:
        return f"Failed to list Bluetooth devices: {e}"


def toggle_night_light(state: str) -> str:
    """
    Enable or disable Night Light mode.
    """
    try:
        if os.name == "nt":  # Windows
            if state.lower() == "on":
                subprocess.run(
                    "powershell -Command \"Start-Process powershell -ArgumentList 'Add-Type -AssemblyName PresentationFramework; [System.Windows.SystemParameters]::NightMode = $true' -Verb RunAs\"",
                    shell=True,
                    check=True,
                )
                return "Night Light has been enabled."
            elif state.lower() == "off":
                subprocess.run(
                    "powershell -Command \"Start-Process powershell -ArgumentList 'Add-Type -AssemblyName PresentationFramework; [System.Windows.SystemParameters]::NightMode = $false' -Verb RunAs\"",
                    shell=True,
                    check=True,
                )
                return "Night Light has been disabled."
            else:
                return "Invalid state. Use 'on' or 'off'."
        else:
            return "Night Light control is supported only on Windows."
    except subprocess.CalledProcessError as e:
        return f"Failed to toggle Night Light: {e}"



def read_screen_contents_aloud(text: str = None) -> str:
    """
    Read aloud the provided text or visible screen contents.
    """
    try:
        if not text:
            # Capture the screen and extract text using OCR
            screen = ImageGrab.grab()
            text = pytesseract.image_to_string(screen)

        # Use text-to-speech to read the text
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return "Reading screen contents aloud."
    except Exception as e:
        return f"Failed to read screen contents: {e}"
    

def schedule_task(task: str, date_time: str) -> str:
    """
    Schedule a task or reminder at a specific date and time.
    Args:
        task (str): The task to be reminded about.
        date_time (str): The date and time in the format 'YYYY-MM-DD HH:MM:SS'.
    """
    try:
        # Parse the date_time string into a datetime object
        schedule_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

        # Add the task to the scheduler
        scheduler.add_job(
            func=send_reminder,
            trigger=DateTrigger(run_date=schedule_time),
            args=[task],
            id=f"reminder_{date_time}",
            replace_existing=True,
        )
        return f"Task '{task}' scheduled for {date_time}."
    except Exception as e:
        return f"Failed to schedule task: {e}"

def send_reminder(task: str):
    """
    Send a reminder when the task is due.
    Args:
        task (str): The task to remind about.
    """
    print(f"Reminder: {task}")  # You can replace this with a notification or sound alert
    speak_response(f"Reminder: {task}")
