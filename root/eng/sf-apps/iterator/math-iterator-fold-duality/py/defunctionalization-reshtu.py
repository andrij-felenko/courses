class ListIterator:
    def __init__(self, head):
        self.cur = head              # стан = решта обходу, згорнута в ОДИН вказівник

    def has_next(self):
        return self.cur is not None

    def next(self):
        node = self.cur
        self.cur = node.next         # δ: крок до наступного стану
        return node.value
