import struct

HMC_ADDR = 0x1E

# Регістри HMC5883L
HMC_CONFIG_A = 0x00
HMC_CONFIG_B = 0x01
HMC_MODE     = 0x02
HMC_DATA     = 0x03   # далі 6 байтів: X(H,L) Z(H,L) Y(H,L)
HMC_ID_A     = 0x0A   # 'H' (0x48)

HMC_LSB_PER_GAUSS = 1090.0


def hmc_detect(i2c):
    # True, якщо чип на 0x1E справді HMC5883L (ID = 'H','4','3')
    ident = i2c.readfrom_mem(HMC_ADDR, HMC_ID_A, 3)
    return ident == b'H43'   # 0x48 0x34 0x33


def hmc_init(i2c):
    i2c.writeto_mem(HMC_ADDR, HMC_CONFIG_A, bytes([0x70]))  # 8 усереднень, 15 Гц
    i2c.writeto_mem(HMC_ADDR, HMC_CONFIG_B, bytes([0x20]))  # ±1.3 Гаус
    i2c.writeto_mem(HMC_ADDR, HMC_MODE,     bytes([0x00]))  # безперервний вимір


def hmc_read_raw(i2c):
    # Кортеж (x, y, z) або None при переповненні / помилці шини
    b = i2c.readfrom_mem(HMC_ADDR, HMC_DATA, 6)
    # Порядок у чипі: X, Z, Y — big-endian (старший байт першим)
    x, z, y = struct.unpack('>hhh', b)
    # -4096 (0xF000) = ADC-переповнення: поле сильніше за обраний діапазон
    if x == -4096 or y == -4096 or z == -4096:
        return None
    return x, y, z


def hmc_to_gauss(raw):
    # Перевести сирий відлік у Гауси (для діагностики / нахилокомпенсації)
    return raw / HMC_LSB_PER_GAUSS
