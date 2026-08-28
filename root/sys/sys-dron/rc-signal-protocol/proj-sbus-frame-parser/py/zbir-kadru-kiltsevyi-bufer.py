# Кільцевий буфер сирих байтів UART. Розмір — степінь двійки,
# щоб замість ділення на модуль обійтися дешевою маскою «& (SIZE-1)».
RB_SIZE = 64
RB_MASK = RB_SIZE - 1

class Ring:
    def __init__(self):
        self.buf = bytearray(RB_SIZE)
        self.head = 0            # куди пише перервання
        self.tail = 0            # звідки читає головний цикл

rb = Ring()

# Викликається З ПЕРЕРВАННЯ UART на кожен прийнятий байт. Мусить бути коротким.
def sbus_uart_isr(byte):
    nxt = (rb.head + 1) & RB_MASK
    if nxt != rb.tail:           # є місце — інакше просто губимо байт
        rb.buf[rb.head] = byte
        rb.head = nxt

# Читає один байт із буфера. Повертає байт або None, якщо буфер порожній.
def rb_get():
    if rb.head == rb.tail:       # порожньо
        return None
    out = rb.buf[rb.tail]
    rb.tail = (rb.tail + 1) & RB_MASK
    return out
