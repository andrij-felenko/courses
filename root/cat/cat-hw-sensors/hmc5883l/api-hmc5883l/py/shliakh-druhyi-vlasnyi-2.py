QMC_ADDR    = 0x0D
QMC_DATA    = 0x00   # X(L,H) Y(L,H) Z(L,H) — LSB першим
QMC_STATUS  = 0x06   # біт 0 = DRDY (дані готові), біт 1 = OVL (переповнення)
QMC_CONFIG1 = 0x09
QMC_RESET   = 0x0B

# ±2 Гаус → 12000 LSb/Gauss; ±8 Гаус → 3000 LSb/Gauss (datasheet QST)
QMC_LSB_PER_GAUSS = 12000.0


def qmc_init(bus) -> None:
    bus.write_reg(QMC_ADDR, 0x0A, 0x80)         # м'яке скидання
    # (у власному HAL тут коротка пауза ~5 мс)
    bus.write_reg(QMC_ADDR, QMC_RESET, 0x01)    # SET/RESET Period — ОБОВ'ЯЗКОВО
    bus.write_reg(QMC_ADDR, QMC_CONFIG1, 0x1D)  # 512x, ±2G, 200Гц, безперервний


def qmc_read_raw(bus):
    """Кортеж (x, y, z) або None: немає даних / переповнення / помилка шини."""
    st = bus.read_regs(QMC_ADDR, QMC_STATUS, 1)[0]
    if not (st & 0x01):        # DRDY=0 → нових даних ще немає
        return None
    b = bus.read_regs(QMC_ADDR, QMC_DATA, 6)
    if len(b) != 6:
        return None
    # little-endian: молодший байт першим
    x, y, z = struct.unpack('<hhh', b)
    if st & 0x02:              # OVL=1 → переповнення діапазону
        return None
    return x, y, z
