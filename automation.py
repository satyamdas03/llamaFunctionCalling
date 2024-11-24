import schedule
import time
import os

def clean_temp_files():
    """
    Clear temporary files from the system.
    """
    os.system("del /q/f/s %temp%\\*")
    return "Temporary files cleared."

def start_automation():
    """
    Schedule automated tasks.
    """
    schedule.every().day.at("03:00").do(clean_temp_files)  # Example: Cleanup temp files daily

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    start_automation()
