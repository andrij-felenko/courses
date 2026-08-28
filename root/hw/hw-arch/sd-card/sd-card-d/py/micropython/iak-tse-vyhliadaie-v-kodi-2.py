# Прочитати один 512-байтовий сектор у buf (bytearray на 512). lba — номер сектора.
# Для SDHC/SDXC адреса = номер сектора; для старих SDSC було б lba*512.
def sd_read_block(spi, cs, lba, buf):
    cs.value(0)
    if sd_cmd(spi, 17, lba, 0xFF) != 0x00:            # CMD17: read single block
        cs.value(1); return -1
    token = 0xFF                                      # чекаємо маркер початку даних
    while token == 0xFF:
        token = _xchg(spi, 0xFF)
    if token != 0xFE:                                 # 0xFE = дані пішли
        cs.value(1); return -2
    spi.readinto(buf, 0xFF)                           # рівно 512 байтів у buf
    _xchg(spi, 0xFF); _xchg(spi, 0xFF)                # два байти CRC -> у SPI відкидаємо
    cs.value(1)
    return 0                                          # сектор у buf
