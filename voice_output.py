import pyttsx3
import re

engine = pyttsx3.init()
engine.setProperty("rate", 165)

def clean_text(text):
    # Remove emojis and links from text for speaking
    text = re.sub(r"https?://\S+", "", text)  # Remove URLs
    text = re.sub(r"[^\w\s.,!?]", "", text)   # Remove emojis and symbols
    return text.strip()

def speak(text):
    text_to_speak = clean_text(text)
    engine.say(text_to_speak)
    engine.runAndWait()
