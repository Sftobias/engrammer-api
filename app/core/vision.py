from ollama import Client as OllamaClient
from app.core.config import settings

ollama_client = OllamaClient(host=settings.OLLAMA_HOST) if settings.OLLAMA_HOST else None
