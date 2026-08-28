from machine import Pin, SPI

spi   = SPI(1, baudrate=10_000_000)  # апаратний вузол: дані + такт
latch = Pin(4, Pin.OUT)              # LATCH — як і раніше, вручну

# Той самий показ байта, але засув віддано апаратному SPI
def show_byte_spi(value):
    spi.write(bytes([value]))        # SPI сам жене 8 бітів + такт
    latch.value(1)                   # защіпка — як і раніше, вручну
    latch.value(0)
