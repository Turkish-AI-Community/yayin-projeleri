import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")


settings = Settings()
