class WbSlave:
    def __init__(self):
        self.adr = 0        # ADR_I — адреса від ведучого
        self.dat_o = 0      # DAT_O — дані, які віддаємо на читання (вихід)
        self.stb = 0        # STB_I — «до мене звертаються зараз»
        self.we = 0         # WE_I  — напрямок
        self.ack = 0        # ACK_O — «готово» (вихід)
        self.mem = [0] * 256
        self.latency = 3    # скільки тактів ще «думати»

    # Викликається щотакту. Модель повільної пам'яті з фіксованою затримкою.
    def tick(self):
        if not self.stb:            # до нас не звертаються — мовчимо, ACK знято
            self.ack = 0
            self.latency = 3        # готуємось до наступного звернення
            return
        if self.latency > 0:        # нас вибрали, але ми ще «думаємо»
            self.latency -= 1
            self.ack = 0            # ведучий побачить 0 і почекає ще такт
            return
        # Час настав: віддаємо/приймаємо слово і піднімаємо ACK рівно на цей такт.
        if self.we:
            self.mem[self.adr & 0xFF] = self.dat_o  # (спрощено; реально — окремий вхід)
        else:
            self.dat_o = self.mem[self.adr & 0xFF]
        self.ack = 1
