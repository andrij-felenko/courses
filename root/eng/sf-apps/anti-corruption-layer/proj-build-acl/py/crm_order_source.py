# acl/crm_order_source.py — реалізація ПОРТУ. Склеює фасад + перекладач.
from domain.order import OrderSource, Order
from acl.crm_facade import CrmOrderFacade
from acl.order_translator import translate_order

class CrmOrderSource(OrderSource):
    def __init__(self, facade: CrmOrderFacade):
        self._facade = facade

    def next(self) -> Order | None:
        dto = self._facade.fetch_next()
        return None if dto is None else translate_order(dto)
