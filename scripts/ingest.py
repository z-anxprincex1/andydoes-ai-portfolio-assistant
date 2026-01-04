import os, glob
from typing import List
import psycopg
from dotenv import load_dotenv
from app.rag import embed_text

load_dotenv()
DB = os.environ["DATABASE_URL"]

CHUNK_CHARS = 900
OVERLAP = 150

def chunk_text(text: str) -> List[str]:
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+CHUNK_CHARS])
        i += (CHUNK_CHARS - OVERLAP)
    return [c.strip() for c in chunks if c.strip()]

def ingest_file(path: str):
    doc_id = path.replace("\\", "/")
    title = os.path.splitext(os.path.basename(path))[0]

    # Try to find a Link: line as url
    url = ""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    for line in text.splitlines():
        if line.lower().startswith("link:"):
            url = line.split(":", 1)[1].strip()
            break

    chunks = chunk_text(text)

    with psycopg.connect(DB) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM kb_chunks WHERE doc_id=%s;", (doc_id,))
            conn.commit()

            for idx, ch in enumerate(chunks):
                emb = embed_text(ch)
                emb_str = "[" + ",".join(f"{x:.8f}" for x in emb) + "]"
                cur.execute(
                    """
                    INSERT INTO kb_chunks (doc_id, title, url, chunk_index, content, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s::vector);
                    """,
                    (doc_id, title, url, idx, ch, emb_str)
                )
            conn.commit()

    print(f"✅ Ingested {doc_id} ({len(chunks)} chunks)")

def main():
    files = glob.glob("kb/**/*.md", recursive=True)
    if not files:
        print("No kb/*.md files found.")
        return
    for f in files:
        ingest_file(f)

if __name__ == "__main__":
    main()
