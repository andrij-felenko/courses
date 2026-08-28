# SPI-режим SD через spidev на Linux (Raspberry Pi тощо).
# spi — spidev.SpiDev; xchg(b) — обміняти один байт: віддати b, забрати відповідь.

def xchg(spi, b):
    return spi.xfer2([b])[0]              # один байт туди й назад

def sd_cmd(spi, cmd, arg, crc):
    xchg(spi, 0xFF)                       # такт «вхолосту» перед командою
    xchg(spi, 0x40 | cmd)                 # стартові біти + номер команди
    xchg(spi, (arg >> 24) & 0xFF); xchg(spi, (arg >> 16) & 0xFF)
    xchg(spi, (arg >> 8) & 0xFF);  xchg(spi, arg & 0xFF)  # 4 байти, старший першим
    xchg(spi, crc | 0x01)                 # CRC потрібен лише для CMD0/CMD8
    for _ in range(8):                    # відповідь приходить за кілька тактів
        r = xchg(spi, 0xFF)
        if (r & 0x80) == 0:               # старший біт 0 -> це валідна R1
            return r
    return 0xFF                           # картка не відповіла

# Розбудити картку й перевести її в SPI-режим. Повертає 0, якщо вдалося.
def sd_init(spi, cs):
    spi.max_speed_hz = 200_000            # 100-400 кГц на час ініціалізації
    cs.high()
    for _ in range(10):                   # >= 74 тактів, CS високий
        xchg(spi, 0xFF)

    cs.low()
    if sd_cmd(spi, 0, 0x00000000, 0x94) != 0x01:  # CMD0: idle
        cs.high(); return -1
    sd_cmd(spi, 8, 0x000001AA, 0x86)      # CMD8: перевірка діапазону живлення (+ 4 байти R7)
    for _ in range(4):
        xchg(spi, 0xFF)

    for _ in range(1000):                 # ACMD41 у циклі — чекаємо готовності
        sd_cmd(spi, 55, 0, 0xFF)          # ACMD = CMD55, потім сама команда
        if sd_cmd(spi, 41, 0x40000000, 0xFF) == 0x00:  # біт HCS=1 (підтримка SDHC)
            cs.high()
            spi.max_speed_hz = 25_000_000  # готово -> можна на повну частоту
            return 0
    cs.high()
    return -1                             # картка так і не вийшла з idle
