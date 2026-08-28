class UartRx:
    """Стан приймача одного байта. Таймер зводить isr() ×16 на біт."""

    def __init__(self, line_read, byte_ready):
        self.line_read = line_read    # уже після Шмітта й синхронізатора: 0/1
        self.byte_ready = byte_ready  # віддати зібраний байт користувачеві
        self.active = False           # чи всередині кадру
        self.tick = 0                 # лічильник тіків 0..15 у межах біта
        self.bit_no = 0               # скільки бітів даних уже зібрано
        self.shifter = 0              # тут накопичується байт

    def isr(self):
        """Викликається локальним таймером 16 разів на кожен біт"""
        s = self.line_read()

        if not self.active:               # чекаємо старт-фронт у спокої
            if s == 0:                    # лінія впала — можливий старт
                self.active = True
                self.tick = 0
                self.bit_no = 0
            return

        self.tick += 1
        if self.tick == 8 and self.bit_no == 0:   # центр старт-біта
            if self.line_read() != 0:             # насправді не 0 → хибний старт
                self.active = False               # скинути, чекати знову
            return

        if self.tick >= 16:               # дійшли центру чергового біта даних
            self.tick = 0
            # голос по центру: три сусідні знімки
            b = majority3(self.line_read(), self.line_read(), self.line_read())
            self.shifter = (self.shifter >> 1) | (b << 7)   # молодший біт уперед
            self.bit_no += 1
            if self.bit_no == 8:          # байт зібрано
                self.byte_ready(self.shifter)   # віддати користувачеві
                self.active = False             # (стоп-біт і перевірку — окремо)
