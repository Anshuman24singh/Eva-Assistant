import os

def is_streamlit_cloud():
    return os.environ.get("STREAMLIT_SERVER_HEADLESS") == "1" or "STREAMLIT_ENV" in os.environ

# Default fallback if voice input isn't available
def get_voice_command():
    print("[🎙️ Voice input disabled on cloud]")
    return ""

if not is_streamlit_cloud():
    try:
        import sounddevice as sd
        import speech_recognition as sr

        def get_voice_command():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("🎙️ Listening...")
                audio = recognizer.listen(source)

            try:
                command = recognizer.recognize_google(audio)
                print("You said:", command)
                return command
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
    except Exception as e:
        print(f"[⚠️ Voice input unavailable: {e}]")
