"""Image serialization to various formats."""
import io


def image_to_bytes(pil_img, fmt="PNG"):
    """Serialize a PIL image to bytes in the given format.

    Args:
        pil_img: PIL.Image.Image to serialize
        fmt: Image format string (e.g. "PNG", "JPEG", "WEBP")

    Returns:
        io.BytesIO: Buffer containing the serialized image
    """
    img_io = io.BytesIO()

    save_kwargs = {}
    if fmt.upper() in ("JPEG", "WEBP"):
        save_kwargs["quality"] = 85
    if fmt.upper() == "PNG":
        save_kwargs["quality"] = 70

    pil_img.save(img_io, fmt, **save_kwargs)
    img_io.seek(0)
    return img_io


# Map format names to MIME types
FORMAT_MIMETYPES = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
    "WEBP": "image/webp",
}
