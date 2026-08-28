# MicroPython, i2c = machine.I2C(...) уже створено. Адреса FT6206-класу — 0x38.
TS_ADDR = 0x38
REG_NUM = 0x02   # кількість активних точок
REG_P1_XH = 0x03  # далі XH, XL, YH, YL для точки 1

buf = i2c.readfrom_mem(TS_ADDR, REG_NUM, 5)  # лічильник + 4 байти точки

touches = buf[0] & 0x0F               # молодші 4 біти — кількість дотиків
if touches > 0:
    # XH: біти 7..6 — прапорець події, біти 3..0 — старші біти X
    x = ((buf[1] & 0x0F) << 8) | buf[2]
    y = ((buf[3] & 0x0F) << 8) | buf[4]
    # тепер (x, y) — сирі координати контролера
