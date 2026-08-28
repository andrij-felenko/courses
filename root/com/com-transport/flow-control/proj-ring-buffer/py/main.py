RB_SIZE = 256                       # степінь двійки → маска замість ділення
RB_MASK = RB_SIZE - 1


class RingBuf:
    def __init__(self):
        self.buf = bytearray(RB_SIZE)
        self.head = 0               # пише ЛИШЕ переривання
        self.tail = 0               # пише ЛИШЕ читач

    def empty(self):
        return self.head == self.tail

    def full(self):
        # наступний head упреться в tail
        return ((self.head + 1) & RB_MASK) == self.tail
