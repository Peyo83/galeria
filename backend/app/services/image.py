import os
import asyncio
from pathlib import Path
from PIL import Image, ImageOps
import io

MEDIA_DIR = Path("media/watercolors")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

def _process_image_sync(file_bytes: bytes, base_filename: str) -> str:
    """Ejecutado dentro de un ThreadPoolExecutor para no bloquear el Event Loop."""
    img = Image.open(io.BytesIO(file_bytes))
    img = ImageOps.exif_transpose(img) # Corregir orientación EXIF
    
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Imagen Principal Optimizada WebP (Max W: 1920px)
    max_size = (1920, 1920)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    main_path = MEDIA_DIR / f"{base_filename}.webp"
    img.save(main_path, "WEBP", quality=85, optimize=True)

    # Thumbnail WebP (Max W: 600px) para Grid/Listados
    thumb = img.copy()
    thumb.thumbnail((600, 600), Image.Resampling.LANCZOS)
    thumb_path = MEDIA_DIR / f"{base_filename}_thumb.webp"
    thumb.save(thumb_path, "WEBP", quality=80, optimize=True)

    return f"watercolors/{base_filename}"

async def save_and_process_image(file_bytes: bytes, base_filename: str) -> str:
    """Punto de entrada asíncrono hacia el pool de hilos."""
    return await asyncio.to_thread(_process_image_sync, file_bytes, base_filename)

async def delete_artwork_images(base_path: str) -> None:
    """Limpia los archivos físicos al eliminar una obra."""
    def _delete_sync():
        full_base = Path("media") / base_path
        main_file = Path(f"{full_base}.webp")
        thumb_file = Path(f"{full_base}_thumb.webp")
        
        if main_file.exists():
            os.remove(main_file)
        if thumb_file.exists():
            os.remove(thumb_file)

    await asyncio.to_thread(_delete_sync)