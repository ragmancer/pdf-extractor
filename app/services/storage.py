import shutil
from pathlib import Path
from typing import BinaryIO

from app.config import settings


def save_original(fileobj: BinaryIO, filename: str) -> str:
    dest = Path(settings.originals_dir) / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    # binary writing
    with open(dest, "wb") as f:
        shutil.copyfileobj(fileobj, f)
    return str(dest)
