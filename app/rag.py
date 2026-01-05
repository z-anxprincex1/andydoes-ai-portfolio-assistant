import os
import requests
from typing import List, Dict, Any, Optional
from .db import get_conn
from .prompts import SYSTEM_PROMPT

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.1")

def embed_text(text: str) -> List[float]:
    r = requests.post(
        f"{OLLAMA_BASE_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["embedding"]

def retrieve_top_k(query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
    emb_str = "[" + ",".join(f"{x:.8f}" for x in query_embedding) + "]"
    sql = """
    SELECT doc_id, title, url, content,
           1 - (embedding <=> %s::vector) AS similarity
    FROM kb_chunks
    ORDER BY embedding <=> %s::vector
    LIMIT %s;
    """
    out = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (emb_str, emb_str, k))
            for doc_id, title, url, content, sim in cur.fetchall():
                out.append({
                    "doc_id": doc_id,
                    "title": title,
                    "url": url,
                    "content": content,
                    "similarity": float(sim),
                })
    return out

def build_context(snips: List[Dict[str, Any]]) -> str:
    parts = []
    for i, s in enumerate(snips, 1):
        parts.append(f"[{i}] doc_id={s['doc_id']} title={s.get('title')}\n{s['content']}")
    return "\n\n".join(parts)

def generate_answer(user_message: str, context: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        msgs.extend(history[-6:])  # keep it short
    msgs.append({"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{user_message}"})

    r = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={"model": CHAT_MODEL, "messages": msgs, "stream": False},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["message"]["content"]

def rag_chat(message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    q_emb = embed_text(message)
    snips = retrieve_top_k(q_emb, k=5)
    context = build_context(snips)
    answer = generate_answer(message, context, history=history)

    seen = set()
    sources = []
    for s in snips:
        if s["doc_id"] in seen:
            continue
        seen.add(s["doc_id"])
        sources.append({"title": s.get("title"), "url": s.get("url"), "doc_id": s["doc_id"]})

    return {"reply": answer, "sources": sources}
