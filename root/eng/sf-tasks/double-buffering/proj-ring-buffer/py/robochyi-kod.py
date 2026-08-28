RB_SIZE = 256                        # степінь двійки → швидка маска
RB_MASK = RB_SIZE - 1


class Ring:
    def __init__(self):
        self.buf = bytearray(RB_SIZE)
        self.head = 0                # writer index
        self.tail = 0                # reader index
        self.count = 0              # зайнято байтів

    # writer: True = записано, False = повно (політика «відкинути новий»)
    def push(self, b):
        if self.count == RB_SIZE:    # повно
            return False
        self.buf[self.head] = b                  # 1) дані
        self.head = (self.head + 1) & RB_MASK    # 2) посунути голову
        self.count += 1
        return True

    # reader: повертає байт або None, якщо порожньо
    def pop(self):
        if self.count == 0:          # порожньо
            return None
        b = self.buf[self.tail]
        self.tail = (self.tail + 1) & RB_MASK
        self.count -= 1
        return b
