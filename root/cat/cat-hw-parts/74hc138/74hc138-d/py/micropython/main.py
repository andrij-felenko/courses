from machine import Pin

# A0, A1, A2 -> три окремі ніжки (у MicroPython немає «порту цілком»)
A = [Pin(0, Pin.OUT), Pin(1, Pin.OUT), Pin(2, Pin.OUT)]

def decoder_select(dev):        # dev = 0..7
    # виставляємо три біти адреси окремо на кожну ніжку
    for i in range(3):
        A[i].value((dev >> i) & 1)

def talk_to_device5():
    decoder_select(5)           # 101 -> Y5 падає в 0 -> ~CS пристрою 5 = 0
    reply = spi.read(1, 0x9F)   # обмін по спільній шині, поки CS5 активний
    decoder_select(0)           # 000 -> тепер активний Y0; пристрій 5 відпущено
    return reply
