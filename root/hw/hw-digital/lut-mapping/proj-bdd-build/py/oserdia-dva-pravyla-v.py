FALSE, TRUE = 0, 1                # два термінали на весь усесвіт — просто числа


class BDD:
    def __init__(self, order):
        self.order = list(order)                        # порядок змінних, згори вниз
        self.rank = {v: i for i, v in enumerate(self.order)}
        self.node = {}                                  # id -> (var, lo, hi)
        self.unique = {}                                # (var, lo, hi) -> id
        self._next = 2                                  # 0 і 1 уже зайняті

    def make_node(self, var, lo, hi):
        if lo == hi:                                    # правило 1: зайве питання
            return lo
        key = (var, lo, hi)
        found = self.unique.get(key)                    # правило 2: без дублікатів
        if found is not None:
            return found
        uid = self._next
        self._next += 1
        self.node[uid] = key
        self.unique[key] = uid
        return uid
