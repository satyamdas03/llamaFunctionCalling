import instructor
from openai import OpenAI
from schemas import FunctionCall
from functions import (
    set_brightness,
    set_volume,
    get_battery,
    get_storage_info,
    open_application,
    search_web,
    toggle_wifi,
    show_connected_wifi,
    toggle_bluetooth,
    list_paired_bluetooth_devices,
    toggle_night_light,
    read_screen_contents_aloud,
)
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Initialize the LLaMA client
client = instructor.from_openai(
    OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key),
    mode=instructor.Mode.JSON,
)

def process_command(user_input: str) -> str:
    """
    Process user input and generate function calls via LLaMA 3.2.
    """
    try:
        # Get LLaMA function result
        function_result = client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct:free",
            response_model=FunctionCall,
            messages=[
                {"role": "system", "content": "You are an AI assistant. You can control system settings and perform tasks. Always provide accurate function names and arguments in your response."},
                {"role": "user", "content": user_input},
            ],
            max_tokens=512,  # Limit output to a reasonable length
        )
        
        # Debugging function name and arguments
        print(f"Function name: {function_result.name}")
        print(f"Arguments: {function_result.arguments}")

        # Match and execute the correct function
        if function_result.name == "set_brightness":
            return set_brightness(function_result.arguments.brightness)
        elif function_result.name == "set_volume":
            return set_volume(function_result.arguments.volume)
        elif function_result.name == "get_battery":
            return get_battery()
        elif function_result.name == "get_storage_info":
            drive = function_result.arguments.drive or "C:"  # Default to C drive
            return get_storage_info(drive)
        elif function_result.name == "open_application":
            app_path = function_result.arguments.app_path or "C:\\Windows\\System32\\notepad.exe"  # Default to Notepad
            return open_application(app_path)
        elif function_result.name == "search_web":
            return search_web(function_result.arguments.query)
        elif function_result.name == "toggle_wifi":
            return toggle_wifi(function_result.arguments.state)
        elif function_result.name == "show_connected_wifi":
            return show_connected_wifi()
        elif function_result.name == "toggle_bluetooth":
            return toggle_bluetooth(function_result.arguments.state)
        elif function_result.name == "list_paired_bluetooth_devices":
            return list_paired_bluetooth_devices()
        elif function_result.name == "toggle_night_light":
            return toggle_night_light(function_result.arguments.state)
        elif function_result.name == "read_screen_contents_aloud":
            return read_screen_contents_aloud(function_result.arguments.text)
        else:
            return "Unknown command. Ensure your input is supported."
    except Exception as e:
        # Handle specific errors like max_tokens and provide a useful response
        if "max_tokens" in str(e):
            return "The output is incomplete due to a max_tokens length limit. Please refine your query."
        return f"An error occurred while processing the command: {e}"
