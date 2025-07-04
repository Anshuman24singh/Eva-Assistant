import streamlit as st
import os
import pickle
import json
from agent.agent import ask_agent
from speak import speak  # New browser-based speak
from voice_input import get_voice_command
from streamlit_lottie import st_lottie

# Constants
MEMORY_FILE = ".streamlit/chat_memory.pkl"
LOTTIE_SPEAKING = "assets/lottie_speaking.json"
LOTTIE_IDLE = "assets/lottie_idle.json"

# App config
st.set_page_config(page_title="EVA Assistant", page_icon="🤖", layout="centered")

# Load CSS
if os.path.exists("frontend/styles.css"):
    with open("frontend/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load Lottie animations
def load_lottie(path):
    with open(path, "r") as f:
        return json.load(f)

lottie_speaking = load_lottie(LOTTIE_SPEAKING)
lottie_idle = load_lottie(LOTTIE_IDLE)

# Session state setup
if "messages" not in st.session_state:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "rb") as f:
            st.session_state.messages = pickle.load(f)
    else:
        st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "text"

if "eva_status" not in st.session_state:
    st.session_state.eva_status = "idle"

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# Sidebar for mode and clearing
with st.sidebar:
    st.title("🎙 EVA Mode")
    st.session_state.mode = st.radio("Choose input mode", ["voice", "text"])
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
        st.rerun()

# EVA Title
st.markdown("<h1 class='eva-title'>EVA</h1>", unsafe_allow_html=True)

# Display Animation
with st.container():
    if st.session_state.eva_status == "speaking":
        st_lottie(lottie_speaking, key="speak", height=180, width=180)
    else:
        st_lottie(lottie_idle, key="idle", height=180, width=180)

# Intro (spoken once)
if not st.session_state.intro_done:
    intro = "Hi! I'm EVA, your smart calendar assistant. I can check your schedule or book appointments."
    speak(intro)
    st.session_state.messages.append({"from": "eva", "message": intro})
    st.session_state.intro_done = True

# Display chat history
for entry in st.session_state.messages:
    who = entry["from"]
    msg = entry["message"]
    bubble = "eva-bubble" if who == "eva" else "user-bubble"
    st.markdown(f"<div class='chat-bubble {bubble}'>{msg}</div>", unsafe_allow_html=True)

# Input handling
user_input = None

# Voice input
if st.session_state.mode == "voice":
    if st.button("🎤 Speak"):
        st.session_state.eva_status = "listening"
        user_input = get_voice_command()
        st.session_state.eva_status = "idle"

        if user_input:
            st.session_state.messages.append({"from": "user", "message": user_input})
            response = ask_agent(user_input)
            st.session_state.messages.append({"from": "eva", "message": response})

            st.session_state.eva_status = "speaking"
            speak(response)
            st.session_state.eva_status = "idle"

            with open(MEMORY_FILE, "wb") as f:
                pickle.dump(st.session_state.messages, f)

            st.rerun()

# Text input
else:
    user_input = st.text_input("💬 Type your message and press Enter", key="input_box")

    if user_input and not st.session_state.get("processed", False):
        st.session_state.processed = True
        st.session_state.messages.append({"from": "user", "message": user_input})
        response = ask_agent(user_input)
        st.session_state.messages.append({"from": "eva", "message": response})

        st.session_state.eva_status = "speaking"
        speak(response)
        st.session_state.eva_status = "idle"

        with open(MEMORY_FILE, "wb") as f:
            pickle.dump(st.session_state.messages, f)

        st.rerun()

# Reset after rerun
if st.session_state.get("processed", False):
    del st.session_state["processed"]
