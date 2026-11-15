"""
Document Q&A API — upload a document, ask questions, get answers grounded in it, with sources.

Run locally:  uvicorn app.main:app --reload     then open http://127.0.0.1:8000/docs
"""
from fastapi import Depends, FastAPI

from app import models  # noqa: F401  (registers tables)
from app.database import Base, engine
from app.rag.providers import get_answerer, get_embedder
from app.routers import auth, documents

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Q&A API (RAG)",
    description=(
        "Upload a PDF or text file, then ask questions about it in plain English. Answers are drawn only "
        "from your document and cite the passages they came from; if the document doesn't contain the "
        "answer, the API says so.\n\nSign up, log in, then click **Authorize** to call the document routes."
    ),
    version="1.0.0",
)
app.include_router(auth.router)
app.include_router(documents.router)


@app.get("/health", tags=["system"])
def health(embedder=Depends(get_embedder), answerer=Depends(get_answerer)):
    """Liveness check that also reports which providers are active (never any keys)."""
    return {"status": "ok", "embeddings": embedder.name, "answerer": answerer.name}
