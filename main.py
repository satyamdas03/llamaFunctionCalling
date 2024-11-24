from fastapi import FastAPI
from llama_integration import process_command
from voice import listen_command, speak_response

app = FastAPI()

@app.post("/control")
def control_system(user_input: str = None):
    """
    API endpoint to process user input (text or voice) and control system functionality.
    """
    if not user_input:
        user_input = listen_command()  # Use voice if no text input
    response = process_command(user_input)
    speak_response(response)  # Speak the response back to the user
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
