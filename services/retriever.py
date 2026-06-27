from qdrant_client import QdrantClient
from services.embedder import get_embedding
from config import settings


def retrieve_chunks(query: str, qdrant: QdrantClient) -> list[str]:
    """
    Embed the query and find the most semantically similar chunks
    from Qdrant. This is our custom retriever — no RetrievalQAChain.
    """
    query_vector = get_embedding(query)

    results = qdrant.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        limit=settings.top_k_results,
    )

    chunks = [hit.payload["text"] for hit in results.points if hit.payload]
    return chunks