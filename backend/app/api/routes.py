import uuid
import shutil
import os
import json
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from elasticsearch import Elasticsearch
from redis import Redis
from app.services.parser import parse_document, chunk_text
from app.core.config import settings

router = APIRouter()

es = Elasticsearch([settings.ELASTICSEARCH_URL])
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

@router.post("/documents/upload")
async def upload(file: UploadFile = File(...)):
    """
    Upload and index a document (PDF or DOCX).
    Validates format, size, extracts text, chunks and indexes to Elasticsearch.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый формат. Разрешены: {ALLOWED_EXTENSIONS}"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    if os.path.getsize(tmp_path) > MAX_FILE_SIZE:
        os.remove(tmp_path)
        raise HTTPException(status_code=400, detail="Файл превышает 20 МБ")

    try:
        text = parse_document(tmp_path, ext)
        chunks = chunk_text(text)
    except Exception as e:
        os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")

    os.remove(tmp_path)

    doc_id = str(uuid.uuid4())
    for i, chunk in enumerate(chunks):
        es.index(
            index="documents",
            body={
                "file_name": file.filename,
                "doc_id": doc_id,
                "chunk_id": f"{doc_id}_{i}",
                "page_number": chunk["page"],
                "text": chunk["text"]
            }
        )

    es.indices.refresh(index="documents")

    return {
        "doc_id": doc_id,
        "file_name": file.filename,
        "chunks_count": len(chunks),
        "status": "indexed"
    }

@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """
    Full-text search with Redis caching (TTL=5 min).
    Uses Elasticsearch multi_match with Russian analyzer.
    """
    cache_key = f"search:{q}:{page}:{size}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    from_offset = (page - 1) * size

    try:
        resp = es.search(
            index="documents",
            body={
                "query": {
                    "multi_match": {
                        "query": q,
                        "fields": ["text"],
                        "type": "best_fields"
                    }
                },
                "highlight": {
                    "fields": {
                        "text": {
                            "pre_tags": ["<mark>"],
                            "post_tags": ["</mark>"],
                            "fragment_size": 300,
                            "number_of_fragments": 1
                        }
                    }
                },
                "from": from_offset,
                "size": size
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")

    results = []
    for hit in resp["hits"]["hits"]:
        src = hit["_source"]
        results.append({
            "chunk_id": src.get("chunk_id", ""),
            "file_name": src.get("file_name", ""),
            "page": src.get("page_number", 0),
            "text": src.get("text", ""),
            "highlight": hit.get("highlight", {}).get("text", [""])[0],
            "score": hit["_score"]
        })

    total = resp["hits"]["total"]["value"]
    out = {
        "results": results,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

    redis_client.setex(cache_key, 300, json.dumps(out))
    return out
