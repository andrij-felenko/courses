class List:
    def __init__(self):
        self._items = []
    def get(self, i):
        return self._items[i]
    def add(self, x):
        self._items.append(x)

# «Незмінний список — це ж різновид списка?» — і тут пастка:
class ImmutableList(List):
    def add(self, x):
        raise TypeError("не можна: список незмінний")   # посилив передумову

# Клієнт, написаний чесно під List, ламається:
def fill(lst: List) -> None:
    for i in range(3):
        lst.add(i)      # на ImmutableList — вибух
