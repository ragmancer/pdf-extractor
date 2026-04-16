import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


@dataclass
class Settings:
    llm_api_url: str | None = os.getenv("LLM_API_URL")
    llm_api_key: str | None = os.getenv("LLM_API_KEY")
    job_storage_dir: str = os.getenv("JOB_STORAGE_DIR", "./data/jobs")
    originals_dir: str = os.getenv("ORIGINALS_DIR", "./data/originals")
    default_expiry_months: int = int(os.getenv("DEFAULT_EXPIRY_MONTHS", "6"))


settings = Settings()

Path(settings.job_storage_dir).mkdir(parents=True, exist_ok=True)
Path(settings.originals_dir).mkdir(parents=True, exist_ok=True)
