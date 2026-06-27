import ollama
from config import settings


def build_prompt(
    context_chunks: list[str],
    history: list[dict],
    user_message: str,
) -> list[dict]:
    """
    Build the full message list for the LLM manually.
    No RetrievalQAChain — we construct the prompt ourselves.
    """
    system_prompt = """You are a helpful assistant. 
Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say "I don't have enough information to answer that."
Do not make up information.

Context:
{context}""".format(
        context="\n\n".join(context_chunks)
    )

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history
    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    return messages


def call_llm(messages: list[dict]) -> str:
    """Send messages to Ollama LLM and return the response text."""
    response = ollama.chat(
        model=settings.ollama_llm_model,
        messages=messages,
    )
    return response["message"]["content"]