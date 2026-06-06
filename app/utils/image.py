"""Image utility helpers: validation, compression, saving."""
import io
import uuid
from pathlib import Path

from PIL import Image

ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP", "BMP"}
MAX_DIM = 1600


def validate_and_compress(raw: bytes) -> tuple[bytes, str]:
    """Validate image bytes and return compressed JPEG bytes + extension."""
    try:
        img = Image.open(io.BytesIO(raw))
        img.verify()
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Invalid image: {exc}") from exc

    img = Image.open(io.BytesIO(raw))
    if (img.format or "").upper() not in ALLOWED_FORMATS:
        raise ValueError(f"Unsupported image format: {img.format}")

    if img.mode != "RGB":
        img = img.convert("RGB")

    # Resize if too large to speed up OCR
    w, h = img.size
    if max(w, h) > MAX_DIM:
        scale = MAX_DIM / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return buf.getvalue(), "jpg"


def save_image(data: bytes, ext: str, directory: str) -> str:
    Path(directory).mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = Path(directory) / filename
    path.write_bytes(data)
    return str(path)
