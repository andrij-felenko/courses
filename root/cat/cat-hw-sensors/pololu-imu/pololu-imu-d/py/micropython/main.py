from machine import I2C

LSM6_ADDR    = 0x6B   # адреса LSM6DS33 на шині
REG_WHO_AM_I = 0x0F
REG_CTRL1_XL = 0x10   # акселерометр
REG_CTRL2_G  = 0x11   # гіроскоп

def lsm6_init(i2c):
    id = i2c.readfrom_mem(LSM6_ADDR, REG_WHO_AM_I, 1)[0]
    if id != 0x69:
        return -1                        # чип не відповів — далі немає сенсу

    # 0x80 = 1.66 кГц, 0x00 = ±2 g  → акселерометр увімкнено
    i2c.writeto_mem(LSM6_ADDR, REG_CTRL1_XL, bytes([0x80]))
    # 0x80 = 1.66 кГц, 0x00 = ±245 °/с → гіроскоп увімкнено
    i2c.writeto_mem(LSM6_ADDR, REG_CTRL2_G, bytes([0x80]))
    return 0
