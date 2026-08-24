import hashlib
import json
import math
import re

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import Note, NoteEmbedding

VECTOR_SIZE = 48


def split_text(text: str, max_chars: int = 500, overlap: int = 80) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + max_chars, len(normalized))
        chunks.append(normalized[start:end])
        if end == len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks


def embed_text(text: str) -> list[float]:
    vector = [0.0] * VECTOR_SIZE
    for token in re.findall(r"[\w一-鿿]+", text.lower()):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % VECTOR_SIZE
        vector[index] += 1.0 if digest[2] % 2 else -1.0
    magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / magnitude, 8) for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def index_note(db: Session, note: Note) -> int:
    db.execute(delete(NoteEmbedding).where(NoteEmbedding.note_id == note.id))
    chunks = split_text(f"{note.title}\n{note.content}")
    for index, content in enumerate(chunks):
        db.add(NoteEmbedding(user_id=note.user_id, note_id=note.id, chunk_index=index, content=content, vector_json=json.dumps(embed_text(content))))
    db.commit()
    return len(chunks)


def retrieve(db: Session, user_id: int, question: str, limit: int = 5) -> list[tuple[Note, str, float]]:
    query_vector = embed_text(question)
    rows = list(db.execute(select(NoteEmbedding, Note).join(Note, Note.id == NoteEmbedding.note_id).where(NoteEmbedding.user_id == user_id)).all())
    ranked = [(note, chunk.content, cosine_similarity(query_vector, json.loads(chunk.vector_json))) for chunk, note in rows]
    return sorted(ranked, key=lambda row: row[2], reverse=True)[:limit]


def answer_question(db: Session, user_id: int, question: str) -> tuple[str, list[tuple[Note, str, float]]]:
    matches = retrieve(db, user_id, question)
    if not matches:
        return "你的知识库里还没有可用于回答的问题内容。先索引几篇笔记吧。", []
    top_note, top_excerpt, _ = matches[0]
    answer = f"根据《{top_note.title}》的笔记：{top_excerpt}"
    return answer, matches
