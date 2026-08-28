REG_READ   = 0xE7   # читати регістр налаштувань 1
REG_WRITE  = 0xE6   # писати регістр налаштувань 1
HEATER_BIT = 0x04   # біт 2 = вмикання нагрівача (HTRE)

# Прочитати регістр налаштувань 1. Повертає байт або None.
def gy21_read_user_reg():
    while not i2c.try_lock():
        pass
    try:
        buf = bytearray(1)
        try:
            i2c.writeto_then_readfrom(GY21_ADDR, bytes([REG_READ]), buf)
        except OSError:
            return None
        return buf[0]
    finally:
        i2c.unlock()


# Увімкнути (on=True) чи вимкнути (on=False) вбудований нагрівач —
# НЕ чіпаючи бітів роздільності (read-modify-write).
def gy21_set_heater(on):
    reg = gy21_read_user_reg()             # 1) прочитати поточний стан
    if reg is None:
        return False

    if on:
        reg |= HEATER_BIT                   # 2) виставити або
    else:
        reg &= ~HEATER_BIT & 0xFF           #    скинути лише біт 2

    while not i2c.try_lock():               # 3) записати назад
        pass
    try:
        try:
            i2c.writeto(GY21_ADDR, bytes([REG_WRITE, reg]))
        except OSError:
            return False
        return True
    finally:
        i2c.unlock()
