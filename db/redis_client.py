import redis
import json
from config import settings

client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
)


def get_redis_client() -> redis.Redis:
    return client


def save_message(session_id: str, role: str, content: str) -> None:
    """Append a message to the conversation history."""
    key = f"chat:{session_id}"
    message = json.dumps({"role": role, "content": content})
    client.lpush(key, message)
    client.expire(key, settings.redis_chat_ttl)


def get_history(session_id: str, limit: int = 10) -> list[dict]:
    """Retrieve the last N messages for a session, oldest first."""
    key = f"chat:{session_id}"
    raw_messages = client.lrange(key, 0, limit - 1)
    messages = [json.loads(m) for m in raw_messages]
    return list(reversed(messages))


def save_booking(session_id: str, booking: dict) -> None:
    """Store booking info as JSON string in Redis."""
    key = f"booking:{session_id}"
    client.set(key, json.dumps(booking))
    print(f"Booking saved: {key} → {booking}")


def get_all_bookings() -> list[dict]:
    """Retrieve all bookings from Redis."""
    keys = client.keys("booking:*")
    print(f"Found booking keys: {keys}")
    bookings = []
    for key in keys:
        raw = client.get(key)
        if raw:
            data = json.loads(raw)
            session_id = key.replace("booking:", "")
            bookings.append({"session_id": session_id, "booking": data})
    return bookings