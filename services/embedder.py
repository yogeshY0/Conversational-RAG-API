import ollama
from config import settings


def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector for a single text string."""
    response = ollama.embeddings(
        model=settings.ollama_embed_model,
        prompt=text,
    )
    return response["embedding"]


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + settings.chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += settings.chunk_size - settings.chunk_overlap

    return [c for c in chunks if c.strip()]  # remove empty chunks