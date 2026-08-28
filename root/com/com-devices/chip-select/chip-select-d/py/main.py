from machine import Pin, SPI

# у кожного веденого — своя ніжка CS, усі за замовчуванням високі
cs_disp  = Pin(10, Pin.OUT, value=1)   # усі CS —
cs_adc   = Pin(9,  Pin.OUT, value=1)   # високі ще
cs_flash = Pin(8,  Pin.OUT, value=1)   # до обміну

spi = SPI(0, baudrate=1_000_000, polarity=1, phase=1,   # старт у режимі АЦП:
          firstbit=SPI.MSB)                             # Mode 3, повільніше

def read_adc():
    spi.init(baudrate=1_000_000, polarity=1, phase=1)  # режим і швидкість АЦП
    cs_adc(0)                          # обрали його: активний нуль
    buf = spi.read(2, 0x00)            # обмін (пише й читає водночас)
    cs_adc(1)                          # відпустили — підняли одразу
    return (buf[0] << 8) | buf[1]
