# Conversational RAG API

A production-style conversational RAG API built with **FastAPI**, **Qdrant**, **Redis**, and **Ollama** (fully local, no API keys needed).

## Architecture
<img width="665" height="432" alt="Screenshot 2026-06-27 at 22 43 15" src="https://github.com/user-attachments/assets/71007908-83c7-4ee8-adac-74ee0647c594" />




## Features

| Feature | Detail |
|---|---|
| Custom RAG | No RetrievalQAChain — retrieval and prompting built from scratch |
| Vector store | Qdrant (no FAISS, no Chroma) |
| Chat memory | Redis — multi-turn conversations via session ID |
| Interview booking | LLM extracts name, email, date, time from natural conversation |
| Fully local | Ollama runs llama3.2 + nomic-embed-text — no OpenAI key needed |
| No UI | Pure REST API — testable via Swagger or curl |

## Tech Stack

| Purpose | Tool |
|---|---|
| API framework | FastAPI |
| LLM | llama3.2 via Ollama |
| Embeddings | nomic-embed-text via Ollama |
| Vector database | Qdrant |
| Chat memory | Redis |
| Validation | Pydantic v2 |

## Project Structure
conversational-rag-api/

├── main.py                        # FastAPI app + lifespan

├── config.py                      # Settings via pydantic-settings

├── routers/
|
│ --  ├── ingest.py                  # POST /ingest

│ --  ├── chat.py                    # POST /chat

│ --  └── booking.py                 # GET /bookings

├── services/

│--   ├── embedder.py                # Chunking + embedding

│-- - ├── retriever.py               # Custom Qdrant vector search

│--   ├── llm.py                     # Prompt builder + LLM caller

│--   ├── memory.py                  # Redis history read/write

│---  └── booking_extractor.py       # LLM-based booking detection

├── db/

│--   ├── qdrant_client.py           # Qdrant connection + collection init

│ --  └── redis_client.py            # Redis connection + helpers

├── models/

│ --  └── schemas.py                 # Pydantic request/response models

├── .env.example

└── requirements.txt

## Setup

### Prerequisites
- Python 3.12+
- Docker
- Ollama

### 1. Clone the repo
```bash
git clone https://github.com/yogeshY0/Conversational-RAG-API.git
cd Conversational-RAG-API
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Qdrant and Redis
```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
docker run -d --name redis -p 6379:6379 redis
```

### 4. Pull Ollama models
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 5. Run the API
```bash
uvicorn main:app --reload
```

### 6. Open Swagger docs
http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ingest` | Upload a PDF or text file |
| POST | `/chat` | Chat with your documents |
| GET | `/bookings` | List all interview bookings |
| GET | `/health` | Health check |

## Usage Examples

### Ingest a document
```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@document.pdf"
```

### Chat with documents
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123", "message": "What is this document about?"}'
```

### Book an interview via natural conversation
```bash
# Turn 1
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123", "message": "I want to book an interview. My name is Yogesh, email yogesh@gmail.com"}'

# Turn 2 — booking auto-detected when all 4 fields collected
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123", "message": "Schedule me for 2026-06-30 at 10:00 AM"}'

# View all bookings
curl http://localhost:8000/bookings
```

### Sample response
```json
{
  "session_id": "abc123",
  "answer": "You have been scheduled for 2026-06-30 at 10:00 AM.",
  "booking_detected": true
}
```

## How It Works

**RAG Pipeline (custom, no RetrievalQAChain):**
1. Document uploaded → chunked into 500-char pieces with 50-char overlap
2. Each chunk embedded via `nomic-embed-text` → stored in Qdrant
3. User asks a question → question embedded → Qdrant cosine similarity search → top 5 chunks retrieved
4. Prompt built manually: `system (context) + history + user message`
5. `llama3.2` generates an answer grounded in retrieved context

**Multi-turn Memory:**
- Each session has a unique `session_id`
- Every turn stored in Redis as a JSON list
- History loaded on every request — LLM always has full context

**Booking Detection:**
- After every chat turn, a second LLM call checks if name + email + date + time are all present
- If complete, booking stored in Redis under `booking:{session_id}`

## License
MIT
