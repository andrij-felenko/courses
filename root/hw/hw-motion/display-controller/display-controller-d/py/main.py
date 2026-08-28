from machine import Pin, SPI

# низькорівневі примітиви платформи: тримають D/C, женуть байти по SPI
spi = SPI(1, baudrate=40_000_000, polarity=0, phase=0)
dc  = Pin(2, Pin.OUT, value=1)   # D/C: 0 → команда, 1 → дані

def send_cmd(c):
    dc(0)                                            # D/C = 0 → команда
    spi.write(bytes([c]))

# задати вікно адрес: CASET (стовпці) + RASET (рядки)
def set_window(x0, y0, x1, y1):
    send_cmd(0x2A)                                   # CASET — діапазон стовпців
    dc(1); spi.write(bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
    send_cmd(0x2B)                                   # RASET — діапазон рядків
    dc(1); spi.write(bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))

def fill_rect(x0, y0, x1, y1, color):
    set_window(x0, y0, x1, y1)
    send_cmd(0x2C)                                   # RAMWR — писати в пам'ять
    px = bytes([color >> 8, color & 0xFF])           # RGB565, старший байт уперед
    dc(1)
    count = (x1 - x0 + 1) * (y1 - y0 + 1)
    for _ in range(count):
        spi.write(px)                                # контролер сам розкладе по вікну
