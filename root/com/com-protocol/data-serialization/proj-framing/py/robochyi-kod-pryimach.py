FLAG = 0x7E       # межа кадру (прапорець HDLC/PPP)
ESC  = 0x7D       # байт екранування
XOR  = 0x20       # маска перекручування екранованого байта
MAX_FRAME = 64    # стеля тіла кадру

ST_WAIT, ST_DATA, ST_ESC = range(3)

class FrameRx:
    def __init__(self):
        self.state = ST_WAIT
        self.buf   = bytearray()     # скільки байтів уже в buf = len(self.buf)

    # згодувати один прийнятий байт; викликати на кожен октет з UART
    def rx_byte(self, b):
        if self.state == ST_WAIT:            # шукаємо початок кадру
            if b == FLAG:                    # знайшли межу — відкриваємо кадр
                self.buf.clear()
                self.state = ST_DATA
            # будь-що інше — сміття, мовчки викидаємо (ресинхронізація)

        elif self.state == ST_DATA:
            if b == FLAG:                    # межа: кадр скінчився
                self._complete()            # звірити CRC й, якщо ок, віддати
                self.buf.clear()             # готуємось до наступного кадру
                self.state = ST_WAIT
            elif b == ESC:                   # далі — екранований байт
                self.state = ST_ESC
            else:                            # звичайний байт даних
                if len(self.buf) < MAX_FRAME:
                    self.buf.append(b)
                else:
                    self.state = ST_WAIT     # ПЕРЕПОВНЕННЯ: скидаємо кадр
                    self.buf.clear()

        elif self.state == ST_ESC:           # попередній байт був ESC
            if b == FLAG:                    # ESC перед межею — кадр порваний
                self.state = ST_WAIT         # відкидаємо, чекаємо нового
                self.buf.clear()
            else:
                d = b ^ XOR                  # перекрутити назад: 0x5E→0x7E, 0x5D→0x7D
                if len(self.buf) < MAX_FRAME:
                    self.buf.append(d)
                    self.state = ST_DATA     # повертаємось у тіло кадру
                else:
                    self.state = ST_WAIT     # переповнення й тут
                    self.buf.clear()
