import re
import threading
import os

# Detect if running on Streamlit Cloud or in headless mode
def is_streamlit_cloud():
    return os.environ.get("STREAMLIT_SERVER_HEADLESS") == "1" or "STREAMLIT_ENV" in os.environ

# Default fallback speak function
def speak(text):
    print(f"[🔇 Speech fallback] {text}")

# Try enabling text-to-speech if not on cloud
try:
    if not is_streamlit_cloud():
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)

        def speak(text):
            engine.say(text)
            engine.runAndWait()
except Exception as e:
    print(f"[⚠️ TTS disabled due to error: {e}]")
