import json
from pathlib import Path
from typing import Any

from app.config import settings


def job_path(job_id: str) -> Path:
    return Path(settings.job_storage_dir) / f"{job_id}.json"


def save_job(job_id: str, data: dict[str, Any]) -> None:
    p = job_path(job_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, default=str, indent=2))


def load_job(job_id: str) -> dict | None:
    p = job_path(job_id)
    if not p.exists():
        return None
    return json.loads(p.read_text())
