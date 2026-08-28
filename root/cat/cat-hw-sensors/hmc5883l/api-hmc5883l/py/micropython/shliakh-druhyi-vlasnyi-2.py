QMC_ADDR    = 0x0D
QMC_DATA    = 0x00   # X(L,H) Y(L,H) Z(L,H) — LSB першим
QMC_STATUS  = 0x06   # біт 0 = DRDY (дані готові), біт 1 = OVL (переповнення)
QMC_CONFIG1 = 0x09
QMC_RESET   = 0x0B

QMC_LSB_PER_GAUSS = 12000.0


def qmc_init(i2c):
    i2c.writeto_mem(QMC_ADDR, 0x0A, bytes([0x80]))         # м'яке скидання
    time.sleep_ms(5)                                       # коротка пауза
    i2c.writeto_mem(QMC_ADDR, QMC_RESET, bytes([0x01]))    # SET/RESET — ОБОВ'ЯЗКОВО
    i2c.writeto_mem(QMC_ADDR, QMC_CONFIG1, bytes([0x1D]))  # 512x, ±2G, 200Гц, безпер.


def qmc_read_raw(i2c):
    # Кортеж (x, y, z) або None: немає даних / переповнення / помилка шини
    st = i2c.readfrom_mem(QMC_ADDR, QMC_STATUS, 1)[0]
    if not (st & 0x01):        # DRDY=0 → нових даних ще немає
        return None
    b = i2c.readfrom_mem(QMC_ADDR, QMC_DATA, 6)
    # little-endian: молодший байт першим
    x, y, z = struct.unpack('<hhh', b)
    if st & 0x02:              # OVL=1 → переповнення діапазону
        return None
    return x, y, z
