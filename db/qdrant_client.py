from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config import settings

client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def get_qdrant_client() -> QdrantClient:
    return client


def init_collection() -> None:
    """Create the documents collection if it doesn't exist."""
    existing = [c.name for c in client.get_collections().collections]

    if settings.qdrant_collection not in existing:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=768,        # nomic-embed-text outputs 768 dimensions
                distance=Distance.COSINE,
            ),
        )
        print(f"Collection '{settings.qdrant_collection}' created.")
    else:
        print(f"Collection '{settings.qdrant_collection}' already exists.")