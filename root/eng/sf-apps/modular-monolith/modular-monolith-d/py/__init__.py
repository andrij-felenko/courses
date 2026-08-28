# warehouse/__init__.py — фасад через __all__
from ._service import Warehouse, make_warehouse   # _service — приватний модуль
__all__ = ["Warehouse", "make_warehouse"]          # видно лише це

# warehouse/_service.py — підкреслення = «не чіпай ззовні»
class _StockTable:                                  # приватна нутрощі
    def hold(self, order_id, qty): ...

class Warehouse:                                    # фасад
    def __init__(self, stock: _StockTable): self._stock = stock
    def reserve(self, order_id, qty):
        return self._stock.hold(order_id, qty)
