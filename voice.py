import speech_recognition as sr
import pyttsx3
import pythoncom  # Required for COM initialization in threaded environments

def listen_command() -> str:
    """
    Capture a voice command from the user.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"User said: {command}")
        return command
    except sr.UnknownValueError:
        return "Sorry, I didn't catch that."
    except sr.RequestError as e:
        return f"Could not request results; {e}"

def speak_response(response: str):
    """
    Speak a given response back to the user.
    """
    try:
        # Initialize COM for multi-threaded environments
        pythoncom.CoInitialize()
        
        # Initialize the text-to-speech engine
        engine = pyttsx3.init()
        engine.say(response)
        engine.runAndWait()
    finally:
        # Ensure COM is uninitialized to clean up resources
        pythoncom.CoUninitialize()
