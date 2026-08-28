# керування nRF24 через spidev (напр. на Raspberry Pi): та сама логіка регістрів
import spidev

R_REGISTER = 0x00
W_REGISTER = 0x20
RX_ADDR_P1 = 0x0B
RX_ADDR_P2 = 0x0C
RX_ADDR_P3 = 0x0D
EN_RXADDR  = 0x02

spi = spidev.SpiDev()
spi.open(0, 0)            # шина 0, пристрій 0 (лінією CE0 керує ядро)
spi.max_speed_hz = 8_000_000
spi.mode = 0             # SPI режим 0: CPOL=0, CPHA=0 — як любить nRF24

def write_reg(reg, value):
    # xfer2 сам опускає й піднімає CS навколо транзакції
    return spi.xfer2([W_REGISTER | reg, value])[0]   # [0] — це STATUS

def write_addr(reg, addr):
    # багатобайтова адреса (для P0/P1): команда + усі байти однією транзакцією
    spi.xfer2([W_REGISTER | reg] + list(addr))

def setup_pipes():
    base = [0xC2, 0xC2, 0xC2, 0xC2, 0xC2]   # адреса P1 (спільний префікс)
    write_addr(RX_ADDR_P1, base)             # повна адреса P1

    # P2, P3 — лише молодший байт; старші 4 позичать у P1
    write_reg(RX_ADDR_P2, 0xC3)              # адреса = C2 C2 C2 C2 C3
    write_reg(RX_ADDR_P3, 0xC4)              # адреса = C2 C2 C2 C2 C4

    # увімкнути труби P1,P2,P3 (біти 1,2,3)
    write_reg(EN_RXADDR, (1 << 1) | (1 << 2) | (1 << 3))
