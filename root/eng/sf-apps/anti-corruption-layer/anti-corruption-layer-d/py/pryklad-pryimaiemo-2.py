# Порт: що домен ВИМАГАЄ від зовнішнього світу. Мова складу, жодного CRM.
from abc import ABC, abstractmethod

class OrderSource(ABC):
    @abstractmethod
    def next(self) -> Order | None:   # дай наступне замовлення як НАШ об'єкт
        ...

# ACL: єдине місце, де живе знання про чужий формат
class CrmOrderAcl(OrderSource):
    def __init__(self, crm: CrmClient):
        self._crm = crm

    def next(self) -> Order | None:
        dto = self._crm.fetch_next()
        if dto is None:
            return None
        return self._translate(dto)            # переклад чужого на наше — тут і лише тут

    def _translate(self, dto: CrmOrderDto) -> Order:
        if dto.qty < 0:
            raise UnsupportedByModel("повернень наш склад не приймає з CRM")
        if dto.status_code not in (1, 2, 3):
            raise UnsupportedByModel(f"статус {dto.status_code} не має відповідника")

        product = self._parse_sku(dto.sku)          # "ART-00417/RED/XL" → Product
        client  = ClientId(dto.client_ref.removeprefix("CL:"))
        return Order(client, product, dto.qty)      # чистий об'єкт нашої моделі

    def _parse_sku(self, sku: str) -> Product:
        article, color, size = sku.split("/")
        return Product(Article(article), Color.parse(color), Size.parse(size))
