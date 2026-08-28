# Розмір — ОБОВ'ЯЗКОВО степінь двійки: тоді обгортання індексу — це
# швидка маска & (SIZE-1), а не дороге ділення % SIZE.
FIFO_SIZE = 256
FIFO_MASK = FIFO_SIZE - 1


class Fifo:
    def __init__(self):
        self.buf = bytearray(FIFO_SIZE)
        self.head = 0   # куди пише продюсер (ISR)
        self.tail = 0   # звідки читає споживач (main)

    # Наступний індекс по колу. Маска замість % — див. нижче про степінь двійки.
    @staticmethod
    def _next(i):
        return (i + 1) & FIFO_MASK

    # «Порожньо» бачить споживач: голова наздогнала хвіст.
    def empty(self):
        return self.head == self.tail

    # «Повно» бачить продюсер: наступна голова вперлась би в хвіст
    # (пожертвувана комірка-роздільник).
    def full(self):
        return self._next(self.head) == self.tail
