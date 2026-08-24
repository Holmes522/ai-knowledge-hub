from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from .config import get_settings

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif",
    ".mp4", ".webm", ".mov",
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".zip",
    ".md", ".txt",
}


def storage_root() -> Path:
    root = Path(get_settings().storage_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def safe_filename(raw_name: str | None) -> str:
    name = Path(raw_name or "attachment").name.strip()
    if not name or name in {".", ".."}:
        raise HTTPException(status_code=400, detail="Filename is required")
    return name


async def save_upload(upload: UploadFile, note_id: int) -> tuple[str, str, int]:
    filename = safe_filename(upload.filename)
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="File type is not allowed")

    data = await upload.read(get_settings().max_upload_size + 1)
    if len(data) > get_settings().max_upload_size:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File is too large")

    relative_path = Path(str(note_id)) / f"{uuid4().hex}{extension}"
    target = storage_root() / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return str(relative_path).replace("\\", "/"), upload.content_type or "application/octet-stream", len(data)


def remove_upload(relative_path: str) -> None:
    root = storage_root()
    target = (root / relative_path).resolve()
    if root not in target.parents:
        return
    target.unlink(missing_ok=True)
