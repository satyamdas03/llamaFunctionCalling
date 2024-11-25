import instructor
from openai import OpenAI
from schemas import FunctionCall
from functions import set_brightness, set_volume, get_battery, get_storage_info, open_application, search_web
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
                {"role": "system", "content": "You are an AI assistant. You can perform system functions like setting brightness and volume, fetching battery and storage info, opening applications, and performing web searches. Always provide accurate function names and arguments in your response."},
                {"role": "user", "content": user_input},
            ],
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
        else:
            return "Unknown command. Ensure your input is supported."
    except Exception as e:
        return f"An error occurred while processing the command: {e}"


