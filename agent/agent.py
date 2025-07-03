import os
import re
import datetime
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from backend.calendar_utils import book_event, get_availability
import dateparser

load_dotenv()

# OpenRouter LLM setup
os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

llm = ChatOpenAI(
    model="deepseek/deepseek-chat-v3-0324:free",  
    temperature=0.4,
)

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

# State memory
last_intent = None
last_time = None
last_duration = 30
last_title = None

def extract_time(text):
    dt = dateparser.parse(text)
    return dt

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

    # Step 1: Exit detection
    if lower in ["exit", "quit", "bye"]:
        return "Goodbye! Take care."

    # Step 2: Extract knowns
    dt = extract_time(message)
    if dt: last_time = dt

    dur = extract_duration(message)
    if dur: last_duration = dur

    title = extract_title(message)
    if title and title.lower() not in ["event", "reminder"]:
        last_title = title

    # Step 3: Detect intent
    if "free" in lower or "available" in lower or "check" in lower:
        last_intent = "check"
    elif "book" in lower or "add" in lower or "schedule" in lower or "set" in lower:
        last_intent = "book"

    # Step 4: Fulfill check
    if last_intent == "check" and last_time:
        end = last_time + datetime.timedelta(minutes=last_duration)
        busy = get_availability(last_time, end)
        if not busy:
            return f"✅ You're free at {last_time.strftime('%I:%M %p')}! Would you like me to add something?"
        else:
            return f"⛔ You're busy at that time."

    # Step 5: Fulfill book
    if last_intent == "book" and all([last_title, last_time]):
        end = last_time + datetime.timedelta(minutes=last_duration)
        busy = get_availability(last_time, end)
        if busy:
            return "⛔ You're already booked at that time."
        link = book_event(last_title, last_time, last_duration)
        # Reset memory
        last_intent = last_time = last_duration = last_title = None
        return f"📅 Event booked: {last_title} — View: {link}"

    # Step 6: Missing info
    if last_intent == "book":
        missing = []
        if not last_title:
            missing.append("event name")
        if not last_time:
            missing.append("time")
        return f"📝 Got it! Could you tell me the {' and '.join(missing)}?"

    # Step 7: Fallback to LLM
    try:
        return chain.invoke({"input": message}).content
    except Exception as e:
        return f"❌ Error: {e}"
