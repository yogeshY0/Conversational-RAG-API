from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.qdrant_client import init_collection
from routers import ingest, chat, booking


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks before the app begins accepting requests."""
    print("Starting up...")
    init_collection()
    yield
    print("Shutting down...")


app = FastAPI(
    title="Conversational RAG API",
    description="Custom RAG with Redis memory, Qdrant vector search, and interview booking.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(booking.router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Check if the API is running."""
    return {"status": "ok"}