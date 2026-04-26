import logging
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .rag_service import RAGService

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

PUBLIC_PATHS = {"/", "/docs", "/redoc", "/openapi.json"}


def generate_api_key() -> str:
    return secrets.token_urlsafe(32)


def _upsert_env_value(env_path: Path, key: str, value: str) -> None:
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    updated = False
    next_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            next_lines.append(f"{key}={value}")
            updated = True
        else:
            next_lines.append(line)

    if not updated:
        next_lines.append(f"{key}={value}")

    env_path.write_text("\n".join(next_lines).strip() + "\n", encoding="utf-8")


def get_or_create_api_key() -> str:
    api_key = os.getenv("API_KEY")
    if api_key:
        return api_key

    api_key = generate_api_key()
    env_path = Path(".env")
    _upsert_env_value(env_path, "API_KEY", api_key)
    os.environ["API_KEY"] = api_key
    logger.warning("Generated API_KEY and saved it to %s", env_path.resolve())
    return api_key


API_KEY = get_or_create_api_key()

app = FastAPI(
    title="Bhoomi RAG API",
    version="1.0.0",
    description="Simple RAG backend API secured with x-api-key.",
)

frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "*").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["x-api-key", "content-type"],
)


@app.middleware("http")
async def api_key_authentication(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    request_api_key = request.headers.get("x-api-key")
    if not request_api_key or not secrets.compare_digest(request_api_key, API_KEY):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthorized. Missing or invalid x-api-key header."},
        )

    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Bhoomi RAG API")
    app.state.rag_service = RAGService()
    logger.info("Bhoomi RAG API is ready")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error for %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def health_check():
    return {"status": "ok", "service": "Bhoomi RAG API"}


@app.get("/ask")
async def ask(query: str = Query(..., min_length=1)):
    rag_service: RAGService | None = getattr(app.state, "rag_service", None)
    if rag_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG service is not ready yet.",
        )

    try:
        return rag_service.ask(query)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        logger.exception("RAG runtime error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
