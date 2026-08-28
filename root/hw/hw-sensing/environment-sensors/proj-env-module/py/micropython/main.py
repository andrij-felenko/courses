from machine import I2C, Pin

ADDR = 0x76                        # SDO=GND; 0x77 якщо SDO=VDDIO
REG_CTRL_HUM, REG_CTRL_MEAS, REG_CONFIG, REG_TEMP = 0xF2, 0xF4, 0xF5, 0xFA

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

def env_setup():
    # ПОРЯДОК важливий: ctrl_hum ПЕРЕД ctrl_meas
    i2c.writeto_mem(ADDR, REG_CONFIG,    bytes([(0x02 << 2) | (0x03 << 5)]))       # filter×4 + пауза 250 мс
    i2c.writeto_mem(ADDR, REG_CTRL_HUM,  bytes([0x01]))                            # osrs_h ×1
    i2c.writeto_mem(ADDR, REG_CTRL_MEAS, bytes([(0x02 << 5) | (0x05 << 2) | 0x03])) # T×2, тиск×16, normal

def read_temp_c(t1, t2, t3):       # t1..t3 — заводські коефіцієнти екземпляра
    b = i2c.readfrom_mem(ADDR, REG_TEMP, 3)         # 3 байти, старший уперед
    raw = (b[0] << 12) | (b[1] << 4) | (b[2] >> 4)  # 20-бітний код
    v1 = (raw / 16384.0 - t1 / 1024.0) * t2
    v2 = (raw / 131072.0 - t1 / 8192.0) ** 2 * t3
    return (v1 + v2) / 5120.0                        # °C
