from machine import Pin, SPI

# низькорівневі примітиви платформи (ніжки CS і DC + шина SPI)
spi = SPI(1, baudrate=40_000_000, polarity=0, phase=0)
cs  = Pin(15, Pin.OUT, value=1)   # вибір кристала (активний нуль)
dc  = Pin(2,  Pin.OUT, value=1)   # рівень ніжки DC

def wr_cmd(c):
    dc(0)                          # DC = 0 → команда
    spi.write(bytes([c]))

def wr_data(b):
    dc(1)                          # DC = 1 → дані
    spi.write(b)

def draw_pixel(x, y, color):
    cs(0)

    wr_cmd(0x2A)                                    # CASET: x..x
    wr_data(bytes([x >> 8, x & 0xFF, x >> 8, x & 0xFF]))

    wr_cmd(0x2B)                                    # RASET: y..y
    wr_data(bytes([y >> 8, y & 0xFF, y >> 8, y & 0xFF]))

    wr_cmd(0x2C)                                    # RAMWR: писати в пам'ять
    wr_data(bytes([color >> 8, color & 0xFF]))      # RGB565, старший байт уперед

    cs(1)
