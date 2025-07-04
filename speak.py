
import re
import threading
import streamlit.components.v1 as components

def speak(text: str, language="en-US", gender="female", rate=1.0, pitch=1.0, volume=1.0):
    components.html(f"""
    <script>
    const speak = () => {{
        const msg = new SpeechSynthesisUtterance({text!r});
        msg.lang = "{language}";
        msg.rate = {rate};
        msg.pitch = {pitch};
        msg.volume = {volume};

        const voices = window.speechSynthesis.getVoices();
        const preferredGender = "{gender}".toLowerCase();

        // Try to match based on name or gender (simplified heuristic)
        msg.voice = voices.find(v => 
            v.lang === "{language}" &&
            (preferredGender === "female" ? /female|woman/i.test(v.name) : /male|man/i.test(v.name))
        ) || voices.find(v => v.lang === "{language}");

        window.speechSynthesis.cancel();  // Stop anything currently speaking
        window.speechSynthesis.speak(msg);
    }}

    // Wait for voices to load
    if (speechSynthesis.onvoiceschanged !== undefined) {{
        speechSynthesis.onvoiceschanged = speak;
    }} else {{
        speak();
    }}
    </script>
    """, height=0)

