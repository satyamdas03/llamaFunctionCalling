import tkinter as tk
from tkinter import messagebox
import requests
import threading
from voice import listen_command, speak_response

# Define the API endpoint
API_URL = "http://127.0.0.1:8000/control"

def send_command(user_input):
    """
    Send the user input to the backend API and get the response.
    """
    try:
        response = requests.post(API_URL, params={"user_input": user_input})
        response.raise_for_status()
        return response.json().get("response", "No response from the API.")
    except Exception as e:
        return f"Error: {e}"

def on_submit():
    """
    Handle the Submit button click to send text input to the API.
    """
    user_input = input_text.get()
    if not user_input:
        messagebox.showwarning("Warning", "Please enter a command.")
        return

    # Clear the response box
    response_text.delete(1.0, tk.END)

    # Get response from the API
    response = send_command(user_input)
    response_text.insert(tk.END, response)

def on_mic():
    """
    Handle the Microphone button click to listen to voice input.
    """
    def listen_and_process():
        try:
            # Clear the response box
            response_text.delete(1.0, tk.END)

            # Listen to the voice command
            user_input = listen_command()
            input_text.set(user_input)

            # Process the command via the API
            response = send_command(user_input)
            response_text.insert(tk.END, response)

            # Speak the response
            speak_response(response)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Run the listening process in a separate thread to avoid UI freezing
    threading.Thread(target=listen_and_process).start()

# Create the Tkinter window
window = tk.Tk()
window.title("AI Assistant")
window.geometry("600x400")

# Input Label
input_label = tk.Label(window, text="Enter Command:")
input_label.pack(pady=5)

# Input Text Box
input_text = tk.StringVar()
input_entry = tk.Entry(window, textvariable=input_text, width=50)
input_entry.pack(pady=5)

# Submit Button
submit_button = tk.Button(window, text="Submit", command=on_submit)
submit_button.pack(pady=5)

# Microphone Button
mic_button = tk.Button(window, text="🎤 Speak", command=on_mic)
mic_button.pack(pady=5)

# Response Label
response_label = tk.Label(window, text="Response:")
response_label.pack(pady=10)

# Response Text Box
response_text = tk.Text(window, height=10, width=70)
response_text.pack(pady=5)

# Run the Tkinter event loop
window.mainloop()
