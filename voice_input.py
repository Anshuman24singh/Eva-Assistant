import warnings
warnings.filterwarnings("ignore", category=UserWarning, message="FP16 is not supported on CPU")
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr

def get_voice_command():
    duration = 5
    filename = "voice_input.wav"
    samplerate = 44100

    print("🎙️ Listening...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    sf.write(filename, recording, samplerate)
    print("✅ Audio saved to voice_input.wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        print("✅ You said:", text)
        return text
    except:
        print("❌ Could not understand audio.")
        return None

