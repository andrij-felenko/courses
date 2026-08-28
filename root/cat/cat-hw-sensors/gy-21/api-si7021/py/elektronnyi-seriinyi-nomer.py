# Читає найстарший байт другої половини серійного номера (SNB3),
# що кодує модель чипа. Повертає байт при успіху або None.
def si7021_read_model_id():
    while not i2c.try_lock():
        pass
    try:
        # -- Друга половина серійного номера: команда 0xFC 0xC9 --
        # Пристрій віддає 6 байтів: SNB3, SNB2, CRC, SNB1, SNB0, CRC.
        # Нам потрібен найперший (SNB3) — він і є ідентифікатор моделі.
        buf = bytearray(6)
        try:
            i2c.writeto_then_readfrom(GY21_ADDR, bytes([0xFC, 0xC9]), buf)
        except OSError:
            return None
        return buf[0]              # <- ідентифікатор моделі
    finally:
        i2c.unlock()


# Зручна обгортка: назвати модель словами.
def gy21_model_name():
    id = si7021_read_model_id()
    return {
        None: "HTU21D або сумісний (не Si70xx)",
        0x15: "Si7021",
        0x14: "Si7020",
        0x0D: "Si7013",
        0x00: "Si70xx (інженерний зразок)",
        0xFF: "Si70xx (інженерний зразок)",
    }.get(id, "невідомий Si70xx")
