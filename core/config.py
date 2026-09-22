import os
from dotenv import load_dotenv

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "").strip()

BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "obras-imagens")

TABLE_PRODUTOS = os.getenv("TABLE_PRODUTOS", "Produtos")
TABLE_CLIENTES = os.getenv("TABLE_CLIENTES", "Clientes")
TABLE_PEDIDOS = os.getenv("TABLE_PEDIDOS", "Pedidos")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

APP_NAME = "ArtStore"


def validar_configuracao() -> str | None:
    if not AZURE_STORAGE_CONNECTION_STRING:
        return (
            "AZURE_STORAGE_CONNECTION_STRING não configurada. "
            "Copie o arquivo .env.example para .env e preencha com a connection "
            "string da sua conta do Azure Storage."
        )
    return None