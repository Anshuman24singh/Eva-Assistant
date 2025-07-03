import pyttsx3
import re
import threading

engine = pyttsx3.init()
engine.setProperty("rate", 165)
engine.setProperty("voice", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0")

def clean_text(text: str) -> str:
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'[^\w\s,.!?]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def speak(text: str):
    clean = clean_text(text)
    try:
        threading.Thread(target=run_voice, args=(clean,), daemon=True).start()
    except RuntimeError:
        pass

def run_voice(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except RuntimeError:
        pass
