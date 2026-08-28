# acl/order_translator.py — ЄДИНЕ місце, де мови CRM і складу зустрічаються.
from crm.dto import CrmOrderDto
from domain.order import Order, Product, Article, Color, Size, ClientId
from domain.errors import UnsupportedByModel

KNOWN_STATUS = {1, 2, 3}  # статуси, що мають відповідник у нас

def translate_order(dto: CrmOrderDto) -> Order:
    # --- чуже без пари: відбій на порозі ---
    if dto.qty < 0:
        raise UnsupportedByModel("повернення (від'ємна кількість) з CRM")
    if dto.qty == 0:
        raise UnsupportedByModel("нульова кількість")
    if dto.status_code not in KNOWN_STATUS:
        raise UnsupportedByModel(f"статус {dto.status_code} без відповідника")

    # --- переклад: народжуємо наші поняття ---
    product = _parse_sku(dto.sku)
    client  = _parse_client(dto.client_ref)
    return Order(client, product, dto.qty)

def _parse_sku(sku: str) -> Product:
    parts = sku.split("/")
    if len(parts) != 3:
        raise UnsupportedByModel(f'SKU не розкладається на 3 частини: "{sku}"')
    article, color, size = parts
    return Product(Article(article), Color.parse(color), Size.parse(size))

def _parse_client(ref: str) -> ClientId:
    if not ref.startswith("CL:"):
        raise UnsupportedByModel(f'client_ref без префікса "CL:": "{ref}"')
    return ClientId(ref[3:])
