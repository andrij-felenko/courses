class Order:
    def __init__(self) -> None:
        self._items: list[Item] = []

    @property
    def items(self) -> list[Item]:
        return self._items      # віддали внутрішній список назовні

# Клієнт тепер порядкує чужими нутрощами:
order.items.append(new_item)   # правило перевірити ЗАБУЛИ
