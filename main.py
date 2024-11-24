from fastapi import FastAPI
from llama_integration import process_command

app = FastAPI()

@app.post("/control")
def control_system(user_input: str):
    """
    API endpoint to process user input and control system functionality.
    """
    result = process_command(user_input)
    return {"response": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
