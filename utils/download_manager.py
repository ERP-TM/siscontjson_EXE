from fastapi import Response
from fastapi.responses import PlainTextResponse
from nicegui import app
import uuid

DOWNLOAD_CACHE = {}  # cache global y único


@app.get("/export_download/{download_id}")
def download_handler(download_id: str):
    file_data = DOWNLOAD_CACHE.pop(download_id, None)

    if file_data is None:
        return PlainTextResponse("Link expirado o inexistente.", status_code=404)

    json_bytes, file_name = file_data

    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )


def save_to_download_cache(json_bytes: bytes, file_name: str) -> str:
    download_id = str(uuid.uuid4())
    DOWNLOAD_CACHE[download_id] = (json_bytes, file_name)
    return f"/export_download/{download_id}"
