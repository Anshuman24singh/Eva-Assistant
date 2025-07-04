import os
import re
import datetime
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from backend.calendar_utils import book_event, get_availability
import dateparser
import streamlit as st

# Load environment variables
load_dotenv()

# Load OpenRouter API key
openrouter_key = None
try:
    openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
    if not openrouter_key:
        raise KeyError("Key missing in st.secrets")
except Exception:
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

# Debug (don't print real key)
print("🔑 st.secrets keys available:", list(st.secrets.keys()))
print("🔑 OpenRouter key loaded from env or secrets?", bool(openrouter_key))

if not openrouter_key:
    raise RuntimeError(
        "❌ OPENROUTER_API_KEY not set. Add it to Streamlit Cloud secrets or `.env` locally."
    )

# Configure OpenRouter for LangChain
os.environ["OPENAI_API_KEY"] = openrouter_key
os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

# Initialize LLM
llm = ChatOpenAI(
    model="deepseek/deepseek-chat-v3-0324:free",
    temperature=0.4,
)

# Prompt template
system_prompt = """
You are EVA, a smart calendar assistant. Be short, polite, and helpful.
- Detect if the user wants to book, check availability, or just view schedule.
- Use natural time parsing (e.g., "tomorrow at 10am", "next Friday", etc).
- If any detail is missing (title, time, or duration), ask for it simply.
- Speak clearly, like a real assistant.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

chain = prompt | llm

# Global memory state
last_intent = None
last_time = None
last_duration = 30
last_title = None

def extract_time(text):
    return dateparser.parse(text)

def extract_duration(text):
    match = re.search(r"(\d+)\s*(minute|min|hour|hr|h)", text.lower())
    if match:
        val = int(match.group(1))
        unit = match.group(2)
        return val * 60 if "hour" in unit or "h" in unit else val
    return 30

def extract_title(text):
    text = text.lower()
    text = re.sub(r"\b(add|book|schedule|reminder|meeting|calendar|event|set|at|on|for|to|with|am|pm|today|tomorrow|please|what|should|minutes?|hours?|check|available|free)\b", "", text)
    text = re.sub(r"\d{1,2}(:\d{2})?\s?(am|pm)?", "", text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.capitalize() if text else "Event"

def ask_agent(message: str) -> str:
    global last_intent, last_time, last_duration, last_title

    print(f"🧠 Agent received: {message}")
    lower = message.lower()

    if lower in ["exit", "quit", "bye"]:
        return "Goodbye! Take care."

    dt = extract_time(message)
    if dt:
        last_time = dt

    dur = extract_duration(message)
    if dur:
        last_duration = dur

    title = extract_title(message)
    if title and title.lower() not in ["event", "reminder"]:
        last_title = title

    if "free" in lower or "available" in lower or "check" in lower:
        last_intent = "check"
    elif "book" in lower or "add" in lower or "schedule" in lower or "set" in lower:
        last_intent = "book"

    if last_intent == "check" and last_time:
        end = last_time + datetime.timedelta(minutes=last_duration)
        busy = get_availability(last_time, end)
        if not busy:
            return f"✅ You're free at {last_time.strftime('%I:%M %p')}! Would you like me to add something?"
        else:
            return f"⛔ You're busy at that time."

    if last_intent == "book" and all([last_title, last_time]):
        end = last_time + datetime.timedelta(minutes=last_duration)
        busy = get_availability(last_time, end)
        if busy:
            return "⛔ You're already booked at that time."
        link = book_event(last_title, last_time, last_duration)
        # Reset state
        response = f"📅 Event booked: {last_title} — View: {link}"
        last_intent = last_time = last_duration = last_title = None
        return response

    if last_intent == "book":
        missing = []
        if not last_title:
            missing.append("event name")
        if not last_time:
            missing.append("time")
        return f"📝 Got it! Could you tell me the {' and '.join(missing)}?"

    try:
        return chain.invoke({"input": message}).content
    except Exception as e:
        return f"❌ Error from assistant: {e}"
