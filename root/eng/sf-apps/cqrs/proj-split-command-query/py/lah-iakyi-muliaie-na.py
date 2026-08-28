# РОУТИНГ читання за свіжістю: свій щойно змінений — з боку запису, решта — зі знімка
class OrderViewRouter:
    def __init__(self, write: OrderRepository, read: OrderReadStore) -> None:
        self._write = write
        self._read = read

    def for_screen(self, order_id: str, just_changed_by_user: bool) -> OrderView:
        if just_changed_by_user:
            o = self._write.by_id(order_id)   # свіжо, повільно — read-your-writes
            return OrderView(id=o.id, customer_name=o.customer_name(),
                             total=o.total(), status=o.status)
        snap = self._read.by_id(order_id)     # швидко, може відставати
        return OrderView(id=snap.id, customer_name=snap.customer_name,
                         total=snap.total, status=snap.status)
