import uuid
from datetime import datetime, timezone

from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

from core import config

_table_service_client: TableServiceClient | None = None


def get_table_service_client() -> TableServiceClient:
    global _table_service_client
    if _table_service_client is None:
        _table_service_client = TableServiceClient.from_connection_string(
            config.AZURE_STORAGE_CONNECTION_STRING
        )
    return _table_service_client


def get_table_client(table_name: str):
    service = get_table_service_client()
    try:
        service.create_table(table_name)
    except ResourceExistsError:
        pass
    return service.get_table_client(table_name)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def criar_produto(dados: dict) -> dict:
    client = get_table_client(config.TABLE_PRODUTOS)
    row_key = str(uuid.uuid4())
    entity = {"PartitionKey": "obra", "RowKey": row_key, **dados, "CriadoEm": _now_iso()}
    client.create_entity(entity=entity)
    return entity


def listar_produtos() -> list:
    client = get_table_client(config.TABLE_PRODUTOS)
    return list(client.query_entities("PartitionKey eq 'obra'"))


def obter_produto(row_key: str):
    client = get_table_client(config.TABLE_PRODUTOS)
    try:
        return client.get_entity(partition_key="obra", row_key=row_key)
    except ResourceNotFoundError:
        return None


def atualizar_produto(row_key: str, dados: dict) -> None:
    client = get_table_client(config.TABLE_PRODUTOS)
    entity = client.get_entity(partition_key="obra", row_key=row_key)
    entity.update(dados)
    client.update_entity(entity, mode="merge")


def excluir_produto(row_key: str) -> None:
    client = get_table_client(config.TABLE_PRODUTOS)
    client.delete_entity(partition_key="obra", row_key=row_key)


def decrementar_estoque(row_key: str, quantidade: int) -> None:
    produto = obter_produto(row_key)
    if not produto:
        return
    nova_qtd = max(0, int(produto.get("Quantidade", 0)) - quantidade)
    atualizar_produto(row_key, {"Quantidade": nova_qtd})


def criar_cliente(dados: dict) -> dict:
    client = get_table_client(config.TABLE_CLIENTES)
    row_key = str(uuid.uuid4())
    entity = {"PartitionKey": "cliente", "RowKey": row_key, **dados, "CriadoEm": _now_iso()}
    client.create_entity(entity=entity)
    return entity


def listar_clientes() -> list:
    client = get_table_client(config.TABLE_CLIENTES)
    return list(client.query_entities("PartitionKey eq 'cliente'"))


def obter_cliente_por_email(email: str):
    client = get_table_client(config.TABLE_CLIENTES)
    email_escapado = email.replace("'", "''")
    resultados = list(
        client.query_entities(f"PartitionKey eq 'cliente' and Email eq '{email_escapado}'")
    )
    return resultados[0] if resultados else None


def atualizar_cliente(row_key: str, dados: dict) -> None:
    client = get_table_client(config.TABLE_CLIENTES)
    entity = client.get_entity(partition_key="cliente", row_key=row_key)
    entity.update(dados)
    client.update_entity(entity, mode="merge")


def excluir_cliente(row_key: str) -> None:
    client = get_table_client(config.TABLE_CLIENTES)
    client.delete_entity(partition_key="cliente", row_key=row_key)


def criar_pedido(dados: dict) -> dict:
    """PartitionKey = e-mail do cliente, para facilitar consultar o histórico dele."""
    client = get_table_client(config.TABLE_PEDIDOS)
    row_key = str(uuid.uuid4())
    entity = {
        "PartitionKey": dados.get("ClienteEmail", "sem-email"),
        "RowKey": row_key,
        **dados,
        "Status": dados.get("Status", "Novo"),
        "CriadoEm": _now_iso(),
    }
    client.create_entity(entity=entity)
    return entity


def listar_pedidos_por_cliente(email: str) -> list:
    client = get_table_client(config.TABLE_PEDIDOS)
    email_escapado = email.replace("'", "''")
    return list(client.query_entities(f"PartitionKey eq '{email_escapado}'"))


def listar_todos_pedidos() -> list:
    client = get_table_client(config.TABLE_PEDIDOS)
    return list(client.query_entities("PartitionKey ne ''"))


def atualizar_status_pedido(partition_key: str, row_key: str, status: str) -> None:
    client = get_table_client(config.TABLE_PEDIDOS)
    entity = client.get_entity(partition_key=partition_key, row_key=row_key)
    entity["Status"] = status
    client.update_entity(entity, mode="merge")