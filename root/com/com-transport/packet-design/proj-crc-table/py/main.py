# Порахувати таблицю один раз (поліном 0x07)
def crc8_init():
    table = []
    for i in range(256):
        crc = i
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
        table.append(crc)
    return table

crc8_table = crc8_init()
