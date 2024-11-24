import instructor
from openai import OpenAI
from schemas import FunctionCall
from functions import set_brightness, set_volume, get_battery, get_storage_info, open_application
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
    function_result = client.chat.completions.create(
        model="meta-llama/llama-3.2-3b-instruct:free",
        response_model=FunctionCall,
        messages=[
            {"role": "system", "content": "You are an AI assistant controlling system functions. Generate function calls based on user requests."},
            {"role": "user", "content": user_input}
        ],
    )

    if function_result.name == "set_brightness":
        return set_brightness(function_result.arguments.brightness)
    elif function_result.name == "set_volume":
        return set_volume(function_result.arguments.volume)
    elif function_result.name == "get_battery":
        return get_battery()
    elif "storage" in user_input:
        return get_storage_info("C:")  # Example for drive C
    elif "open" in user_input:
        if "notepad" in user_input:
            return open_application("C:\\Windows\\System32\\notepad.exe")
    else:
        return "Sorry, I didn't understand that."
