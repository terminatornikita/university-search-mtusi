from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from elasticsearch import Elasticsearch
from app.core.config import settings

app = FastAPI(
    title="University Knowledge Search API",
    description="Интеллектуальная поисковая система по внутренней базе знаний МТУСИ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize Elasticsearch index with Russian analyzer."""
    es = Elasticsearch([settings.ELASTICSEARCH_URL])

    if not es.indices.exists(index="documents"):
        es.indices.create(
            index="documents",
            body={
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "analyzer": {
                            "ru_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": ["lowercase", "russian_stop", "russian_stemmer"]
                            }
                        },
                        "filter": {
                            "russian_stop": {
                                "type": "stop",
                                "stopwords": "_russian_"
                            },
                            "russian_stemmer": {
                                "type": "stemmer",
                                "language": "russian"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "text": {
                            "type": "text",
                            "analyzer": "ru_analyzer"
                        },
                        "file_name": {"type": "keyword"},
                        "doc_id": {"type": "keyword"},
                        "chunk_id": {"type": "keyword"},
                        "page_number": {"type": "integer"}
                    }
                }
            }
        )
