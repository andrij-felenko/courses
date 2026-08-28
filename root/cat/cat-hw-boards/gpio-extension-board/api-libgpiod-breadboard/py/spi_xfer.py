# spi_xfer.py — повнодуплексний обмін по SPI0, chip-enable CE0 (/dev/spidev0.0)
# постав:  pip install spidev
import spidev

spi = spidev.SpiDev()
spi.open(0, 0)                 # SPI0, CE0 = GPIO8 (штир 24) → /dev/spidev0.0

# параметри шини: режим 0, 8 біт на слово, 1 МГц (звіряйте з даташитом пристрою)
spi.mode = 0b00                # SPI_MODE_0
spi.bits_per_word = 8
spi.max_speed_hz = 1000000

# xfer2 і є повний дуплекс: скільки байтів шлемо (tx), стільки й приходить (rx).
# другий байт 0x00 — порожній такт, під який пристрій висуне відповідь.
tx = [0x9F, 0x00]              # напр. команда «read ID» + порожній такт
rx = spi.xfer2(tx)            # поки жене такт, tx їде, rx приходить

print(f"прийнято: 0x{rx[0]:02X} 0x{rx[1]:02X}")
spi.close()
