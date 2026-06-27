import json
import ollama
from datetime import datetime
from config import settings


BOOKING_PROMPT = """
Look at this conversation history carefully.
If the user has provided ALL FOUR of these details for an interview booking:
- name
- email
- date (convert any relative date like "Monday", "tomorrow" to YYYY-MM-DD format based on today's date which is {today})
- time (in HH:MM 24-hour format)

Then extract them and return ONLY a JSON object like this:
{{"name": "...", "email": "...", "date": "YYYY-MM-DD", "time": "HH:MM"}}

If any of the four details are missing, return ONLY the word: null

Conversation:
{history}

Return ONLY the JSON object or the word null. No explanation. No extra text.
"""


def extract_booking(history: list[dict]) -> dict | None:
    """
    Use LLM to detect if a complete booking exists in the conversation.
    Returns a dict with booking info or None if incomplete.
    """
    if not history:
        return None

    formatted_history = "\n".join(
        f"{turn['role'].upper()}: {turn['content']}" for turn in history
    )

    today = datetime.now().strftime("%Y-%m-%d")
    prompt = BOOKING_PROMPT.format(history=formatted_history, today=today)

    response = ollama.chat(
        model=settings.ollama_llm_model,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response["message"]["content"].strip()

    if raw.lower() == "null" or not raw:
        return None

    try:
        booking = json.loads(raw)
        required_fields = {"name", "email", "date", "time"}
        if required_fields.issubset(booking.keys()):
            return booking
        return None
    except json.JSONDecodeError:
        return None