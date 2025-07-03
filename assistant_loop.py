import sys
from voice_input import get_voice_command
from agent.agent import ask_agent
from speak import speak

def main():
    print("🤖 EVA is ready to help you.")
    speak("Hi! I'm EVA, your smart calendar assistant. I can check your schedule or help you book meetings.")

    mode = input("🎙️ Press [v] for voice or [t] for text input: ").strip().lower()

    while True:
        if mode == "v":
            print("🎙️ Listening for 5 seconds...")
            user_input = get_voice_command()
            if not user_input:
                print("😕 Didn't catch that. Try again.")
                continue
        elif mode == "t":
            user_input = input("✍️ You: ")
        else:
            print("⚠️ Invalid input. Press 'v' or 't'.")
            continue

        if not user_input:
            continue

        print(f"✅ You said: {user_input}")

        # Exit condition
        if user_input.strip().lower() in ["exit", "quit", "bye"]:
            goodbye = "Goodbye! Take care."
            print("👋 " + goodbye)
            speak(goodbye)
            sys.exit(0)

        # Get response from agent
        response = ask_agent(user_input)

        if response:
            print(f"🧠 EVA: {response}")
            speak(response)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Exiting EVA.")
        speak("Goodbye! Take care.")
        sys.exit(0)
