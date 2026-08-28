# Прочитати один 512-байтовий сектор. lba — номер сектора; повертає bytes на 512.
# Для SDHC/SDXC адреса = номер сектора; для старих SDSC було б lba*512.
def sd_read_block(spi, cs, lba):
    cs.low()
    if sd_cmd(spi, 17, lba, 0xFF) != 0x00:            # CMD17: read single block
        cs.high(); raise IOError("CMD17 failed")
    token = 0xFF                                      # чекаємо маркер початку даних
    while token == 0xFF:
        token = xchg(spi, 0xFF)
    if token != 0xFE:                                 # 0xFE = дані пішли
        cs.high(); raise IOError("bad data token")
    buf = bytes(spi.readbytes(512))                   # рівно 512 байтів
    xchg(spi, 0xFF); xchg(spi, 0xFF)                  # два байти CRC -> у SPI відкидаємо
    cs.high()
    return buf                                        # сектор
