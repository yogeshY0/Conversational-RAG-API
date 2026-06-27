from db.redis_client import save_message, get_history


def load_history(session_id: str) -> list[dict]:
    """Load conversation history for a session from Redis."""
    return get_history(session_id)


def store_turn(session_id: str, user_message: str, assistant_reply: str) -> None:
    """Store both sides of a conversation turn in Redis."""
    save_message(session_id, "user", user_message)
    save_message(session_id, "assistant", assistant_reply)