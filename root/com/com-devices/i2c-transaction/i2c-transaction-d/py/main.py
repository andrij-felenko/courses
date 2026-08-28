import struct
from machine import I2C           # MicroPython: та сама шина на рівні HAL

MPU_ADDR   = 0x68                 # 7-бітна адреса давача на шині
REG_XOUT_H = 0x3B                 # старший байт осі X (далі X_L, Y_H … поспіль)

def read_accel_x(i2c: I2C) -> int:
    """Прочитати 16-бітну вісь X акселерометра."""
    # Фаза 1: вказати покажчик на регістр 0x3B. stop=False → буде повторний старт.
    i2c.writeto(MPU_ADDR, bytes([REG_XOUT_H]), False)

    # Фаза 2: Sr + адреса з R, читаємо 2 байти поспіль (авто-інкремент покажчика).
    raw = i2c.readfrom(MPU_ADDR, 2)   # raw[0] = 0x3B (старший), raw[1] = 0x3C (молодший)

    # Зібрати знакове значення: '>h' = big-endian, старший байт першим, знаковий int16.
    return struct.unpack(">h", raw)[0]
