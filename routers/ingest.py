from fastapi import APIRouter, UploadFile, File, Depends
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from services.embedder import get_embedding, chunk_text
from db.qdrant_client import get_qdrant_client
from models.schemas import IngestResponse
from config import settings
import pypdf
import uuid
import io

router = APIRouter(prefix="/ingest", tags=["Ingest"])


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file."""
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    return " ".join(page.extract_text() or "" for page in reader.pages)


@router.post("", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    qdrant: QdrantClient = Depends(get_qdrant_client),
) -> IngestResponse:
    """
    Upload a PDF or text file, chunk it, embed each chunk,
    and store in Qdrant vector database.
    """
    file_bytes = await file.read()

    # Extract text based on file type
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    else:
        text = file_bytes.decode("utf-8")

    # Chunk the text
    chunks = chunk_text(text)

    # Embed each chunk and build Qdrant points
    points = []
    for chunk in chunks:
        vector = get_embedding(chunk)
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"text": chunk, "filename": file.filename},
        )
        points.append(point)

    # Store all points in Qdrant
    qdrant.upsert(
        collection_name=settings.qdrant_collection,
        points=points,
    )

    return IngestResponse(
        message=f"Successfully ingested '{file.filename}'",
        chunks_stored=len(chunks),
    )