import uuid
from io import BytesIO

from azure.storage.blob import BlobServiceClient, ContentSettings

from core import config

_blob_service_client: BlobServiceClient | None = None


def get_blob_service_client() -> BlobServiceClient:
    global _blob_service_client
    if _blob_service_client is None:
        _blob_service_client = BlobServiceClient.from_connection_string(
            config.AZURE_STORAGE_CONNECTION_STRING
        )
    return _blob_service_client


def ensure_container():
    client = get_blob_service_client()
    container_client = client.get_container_client(config.BLOB_CONTAINER_NAME)
    if not container_client.exists():
        container_client.create_container(public_access="blob")
    return container_client


def upload_image(file_bytes: bytes, original_filename: str, content_type: str = "image/jpeg") -> str:
    container_client = ensure_container()
    extension = original_filename.split(".")[-1].lower() if "." in original_filename else "jpg"
    blob_name = f"{uuid.uuid4().hex}.{extension}"
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(
        BytesIO(file_bytes),
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )
    return blob_client.url


def delete_image(blob_url: str) -> None:
    """Remove uma imagem do Blob Storage a partir da sua URL. Falhas são ignoradas."""
    if not blob_url:
        return
    try:
        blob_name = blob_url.split("/")[-1].split("?")[0]
        container_client = ensure_container()
        container_client.delete_blob(blob_name)
    except Exception:
        pass
