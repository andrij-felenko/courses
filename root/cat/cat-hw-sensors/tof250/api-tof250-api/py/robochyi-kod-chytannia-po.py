from machine import I2C, Pin

TOF_ADDR = 0x52     # 7-бітна адреса (байт 0xA4 → 0x52)
REG_DIST = 0x00     # відстань, 2 байти (сира чи згладжена — за режимом s3-x#)

i2c = I2C(0, scl=Pin(22), sda=Pin(21))   # типові виводи ESP32

def tof_read_distance():
    """16-бітна відстань із регістра 0x00. None = помилка."""
    try:
        # записуємо номер регістра, потім читаємо 2 байти
        raw = i2c.readfrom_mem(TOF_ADDR, REG_DIST, 2)
    except OSError:
        return None                        # модуль не підтвердив адресу
    hi, lo = raw[0], raw[1]                 # старший байт приходить першим
    return (hi << 8) | lo                   # склали → відстань у мм
