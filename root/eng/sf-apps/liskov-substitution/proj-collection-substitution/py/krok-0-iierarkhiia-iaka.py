class ArrayList:
    def __init__(self):
        self._items = []

    def get(self, i):        return self._items[i]
    def size(self) -> int:   return len(self._items)
    def add(self, x) -> None:
        self._items.append(x)

# «Незмінний список — різновид списка?» — і тут закладено пастку:
class ImmutableList(ArrayList):
    def __init__(self, initial):
        super().__init__()
        self._items = list(initial)        # наповнили раз, при створенні

    def add(self, x) -> None:
        raise TypeError("список незмінний: додавати не можна")
