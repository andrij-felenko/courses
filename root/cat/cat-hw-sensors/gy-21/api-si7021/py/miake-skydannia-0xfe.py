# М'яке скидання давача у стан за замовчуванням.
def gy21_reset():
    while not i2c.try_lock():
        pass
    try:
        try:
            i2c.writeto(GY21_ADDR, bytes([0xFE]))
            ok = True
        except OSError:
            ok = False
    finally:
        i2c.unlock()
    time.sleep(0.015)   # давачу треба ~15 мс на перезавантаження
    return ok
