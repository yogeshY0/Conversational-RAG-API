# Conversational RAG API

A production-style RAG API built with FastAPI, Qdrant, Redis, and Ollama.

## Features
- Custom RAG pipeline (no RetrievalQAChain)
- Redis-backed multi-turn conversation memory
- Qdrant vector search (no FAISS/Chroma)
- Interview booking detection via LLM
- Fully local — no OpenAI key needed (uses Ollama)

## Tech Stack
| Purpose | Tool |
|---|---|
| API | FastAPI |
| LLM | llama3.2 via Ollama |
| Embeddings | nomic-embed-text via Ollama |
| Vector DB | Qdrant |
| Memory | Redis |

## Setup

### 1. Install dependencies
pip install -r requirements.txt

### 2. Start Qdrant and Redis
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
docker run -d --name redis -p 6379:6379 redis

### 3. Pull Ollama models
ollama pull llama3.2
ollama pull nomic-embed-text

### 4. Run the API
uvicorn main:app --reload

### 5. Open Swagger docs
http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /ingest | Upload a PDF or text file |
| POST | /chat | Chat with your documents |
| GET | /bookings | List all interview bookings |
| GET | /health | Health check |

## Usage Example

### Ingest a document
curl -X POST http://localhost:8000/ingest -F "file=@document.pdf"

### Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123", "message": "What is this document about?"}'

### Book an interview via chat
Send messages naturally — the LLM extracts name, email, date, and time automatically.
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123", "message": "I am Yogesh, yogesh@gmail.com, book me for 2026-06-30 at 10:00 AM"}'
