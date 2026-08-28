# перевірити, що на шині справді MPU-6050
def mpu_present():
    try:
        id = mpu_read(REG_WHO, 1)[0]
    except OSError:
        return False
    return id == 0x68                        # сталий код саме цього чіпа

# розбудити чіп і виставити діапазон ±8g (AFS = 0b10 у бітах 4:3)
def mpu_begin():
    mpu_write(REG_PWR, 0x00)                  # вийти зі сну
    cfg = mpu_read(REG_CFG, 1)[0]            # читай…
    cfg = (cfg & ~0x18) | (0b10 << 3)        # …зміни поле AFS…
    mpu_write(REG_CFG, cfg)                   # …запиши
