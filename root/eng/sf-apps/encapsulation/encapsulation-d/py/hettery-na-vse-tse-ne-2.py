class Order:
    def __init__(self) -> None:
        self._items: list[Item] = []
        self._closed = False

    def add_item(self, it: Item) -> None:
        if self._closed:
            raise RuntimeError("замовлення закрите")   # правило всередині
        self._items.append(it)

    @property
    def item_count(self) -> int:      # назовні — факт, не нутрощі
        return len(self._items)

order.add_item(new_item)   # перевірка вже застосована, обійти нема як
