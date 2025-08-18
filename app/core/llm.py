from openai import OpenAI
from app.core.config import settings
import os

if settings.OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)