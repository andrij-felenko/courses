# Бітовий запис LSB-first (як у GIF): код width бітів дописуємо до акумулятора.
class BitWriter:
    def __init__(self):
        self.out = bytearray()
        self.acc = 0
        self.nbits = 0

    def put(self, code, width):
        self.acc |= code << self.nbits         # молодші біти коду — першими
        self.nbits += width
        while self.nbits >= 8:                  # вивантажуємо повні байти
            self.out.append(self.acc & 0xFF)
            self.acc >>= 8
            self.nbits -= 8

    def flush(self):
        # наприкінці: якщо лишилися біти (nbits>0) — дописати останній неповний байт.
        if self.nbits > 0:
            self.out.append(self.acc & 0xFF)
            self.acc = 0
            self.nbits = 0
