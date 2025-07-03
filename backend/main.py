# backend/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

from calendar_utils import get_availability, book_event

app = FastAPI()

# Enable CORS so Streamlit frontend can access it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Request body schemas
# -------------------------------

class AvailabilityRequest(BaseModel):
    start: str  # ISO format datetime
    end: str    # ISO format datetime

class BookingRequest(BaseModel):
    summary: str
    start: str           # ISO format datetime
    duration_minutes: int


# -------------------------------
# Routes
# -------------------------------

@app.get("/")
def root():
    return {"message": "TailorTalk Calendar API is live ✅"}

@app.post("/availability")
def check_availability(req: AvailabilityRequest):
    try:
        start_dt = datetime.fromisoformat(req.start)
        end_dt = datetime.fromisoformat(req.end)
        busy = get_availability(start_dt, end_dt)
        return {"busy_slots": busy}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/book")
def book(req: BookingRequest):
    try:
        start_dt = datetime.fromisoformat(req.start)
        link = book_event(req.summary, start_dt, req.duration_minutes)
        return {"message": "Event created ✅", "link": link}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
