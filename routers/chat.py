from fastapi import APIRouter, Depends
from qdrant_client import QdrantClient
from db.qdrant_client import get_qdrant_client
from db.redis_client import save_booking
from services.retriever import retrieve_chunks
from services.llm import build_prompt, call_llm
from services.memory import load_history, store_turn
from services.booking_extractor import extract_booking
from models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    qdrant: QdrantClient = Depends(get_qdrant_client),
) -> ChatResponse:
    """
    Main conversational RAG endpoint.
    1. Load history from Redis
    2. Retrieve relevant chunks from Qdrant
    3. Build prompt manually
    4. Call LLM
    5. Store turn in Redis
    6. Check for booking intent
    """
    # Step 1: Load conversation history
    history = load_history(request.session_id)

    # Step 2: Retrieve relevant chunks from Qdrant
    chunks = retrieve_chunks(request.message, qdrant)

    # Step 3: Build prompt manually (no RetrievalQAChain)
    messages = build_prompt(
        context_chunks=chunks,
        history=history,
        user_message=request.message,
    )

    # Step 4: Call LLM
    answer = call_llm(messages)

    # Step 5: Store this turn in Redis
    store_turn(request.session_id, request.message, answer)

    # Step 6: Check if conversation contains a complete booking
    updated_history = load_history(request.session_id)
    booking = extract_booking(updated_history)
    booking_detected = False

    if booking:
        save_booking(request.session_id, booking)
        booking_detected = True

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
        booking_detected=booking_detected,
    )