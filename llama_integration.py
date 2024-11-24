import instructor
from openai import OpenAI
from schemas import FunctionCall
from functions import set_brightness, set_volume, get_battery
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
            {"role": "system", "content": "You are an AI assistant controlling system brightness, volume, and battery status. Generate function calls based on user requests."},
            {"role": "user", "content": user_input}
        ],
    )

    if function_result.name == "set_brightness":
        return set_brightness(function_result.arguments.brightness)
    elif function_result.name == "set_volume":
        return set_volume(function_result.arguments.volume)
    elif function_result.name == "get_battery":
        return get_battery()
    else:
        return "Unknown command"
