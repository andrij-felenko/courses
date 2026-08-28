import struct

# ── Об'єкт шини реалізуєш під свою платформу (SMBus, periphery, тощо) ──
# bus.write_reg(addr, reg, val)          -> запис одного байта
# bus.read_regs(addr, reg, n) -> bytes   -> читання n байтів з автоінкрементом

HMC_ADDR = 0x1E

# Регістри HMC5883L
HMC_CONFIG_A = 0x00
HMC_CONFIG_B = 0x01
HMC_MODE     = 0x02
HMC_DATA     = 0x03   # далі 6 байтів: X(H,L) Z(H,L) Y(H,L)
HMC_ID_A     = 0x0A   # 'H' (0x48)

# Підсилення для типового ±1.3 Гаус (Config B = 0x20): 1090 LSb/Gauss
HMC_LSB_PER_GAUSS = 1090.0


def hmc_detect(bus) -> bool:
    """True, якщо чип на 0x1E справді HMC5883L (ID = 'H','4','3')."""
    ident = bus.read_regs(HMC_ADDR, HMC_ID_A, 3)
    return ident == b'H43'   # 0x48 0x34 0x33


def hmc_init(bus) -> None:
    bus.write_reg(HMC_ADDR, HMC_CONFIG_A, 0x70)   # 8 усереднень, 15 Гц
    bus.write_reg(HMC_ADDR, HMC_CONFIG_B, 0x20)   # ±1.3 Гаус
    bus.write_reg(HMC_ADDR, HMC_MODE,     0x00)   # безперервний вимір


def hmc_read_raw(bus):
    """Кортеж (x, y, z) або None при переповненні / помилці шини."""
    b = bus.read_regs(HMC_ADDR, HMC_DATA, 6)
    if len(b) != 6:
        return None
    # Порядок у чипі: X, Z, Y — big-endian (старший байт першим)
    x, z, y = struct.unpack('>hhh', b)
    # -4096 (0xF000) = ADC-переповнення: поле сильніше за обраний діапазон
    if -4096 in (x, y, z):
        return None
    return x, y, z


def hmc_to_gauss(raw: int) -> float:
    """Перевести сирий відлік у Гауси (для діагностики / нахилокомпенсації)."""
    return raw / HMC_LSB_PER_GAUSS
