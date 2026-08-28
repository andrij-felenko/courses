SBUS_LEN    = 25
SBUS_HEADER = 0x0F
SBUS_FOOTER = 0x00

ST_SEEK, ST_COLLECT = 0, 1

class SbusParser:
    def __init__(self):
        self.state = ST_SEEK
        self.frame = bytearray(SBUS_LEN)
        self.idx = 0             # скільки байтів кадру вже набрано

ps = SbusParser()

# Прожовує все, що накопичилось у кільцевому буфері. Коли зібрано цілий
# валідний кадр — повертає його копію (bytes); інакше None (можна кликати
# повторно, доки вертає кадр: за один прохід кадрів може набратися кілька).
def sbus_poll():
    b = rb_get()
    while b is not None:
        if ps.state == ST_SEEK:
            # У пошуку старту викидаємо все, крім заголовка.
            if b == SBUS_HEADER:
                ps.frame[0] = b
                ps.idx = 1
                ps.state = ST_COLLECT

        elif ps.state == ST_COLLECT:
            ps.frame[ps.idx] = b
            ps.idx += 1
            if ps.idx == SBUS_LEN:
                # Кадр набрано повністю — перевіряємо хвіст.
                ps.state = ST_SEEK               # хай там що — далі знову шукаємо старт
                if ps.frame[SBUS_LEN - 1] == SBUS_FOOTER:
                    return bytes(ps.frame)       # валідний кадр
                # Хвіст не 0x00 → десинхрон. Кадр викидаємо, лишаємось у SEEK.

        b = rb_get()
    return None   # цілого кадру поки нема
