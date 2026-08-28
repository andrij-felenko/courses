from dataclasses import dataclass

# МОДЕЛЬ ЧИТАННЯ: денормалізований знімок, усе для картки в одному рядку.
@dataclass
class OrderReadModel:
    id: str
    user_id: str
    customer_name: str    # ← уже склеєно, жодного JOIN на читанні
    total: float
    status: str
    updated_at: float     # коли знімок востаннє наздогнав запис

class OrderReadStore:
    def __init__(self, kv: KeyValueDb) -> None:   # окреме сховище під читання
        self._kv = kv

    def by_id(self, order_id: str) -> OrderReadModel | None:
        return self._kv.get(f"order:{order_id}")  # один доторок за ключем

    def list_by_user(self, user_id: str) -> list[OrderReadModel]:
        return self._kv.get_by_index("order_by_user", user_id)  # готовий індекс

    # сюди пише ЛИШЕ проєкція (крок 3), не бізнес-код
    def upsert(self, m: OrderReadModel) -> None:
        self._kv.put(f"order:{m.id}", m)
        self._kv.index("order_by_user", m.user_id, m.id)
