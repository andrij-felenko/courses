# ── CRC8/DVB-S2, поліном 0xD5 ────────────────────────────────────────────────
# Таблиця на 256 входів; будуємо один раз, далі кожен байт — одна вибірка.
def _build_crc8_table():
    table = []
    for i in range(256):
        crc = i
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
        table.append(crc)
    return table

_CRC8_TABLE = _build_crc8_table()

def crsf_crc8(data):
    crc = 0
    for byte in data:
        crc = _CRC8_TABLE[crc ^ byte]
    return crc
