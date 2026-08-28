def build_table():
    """256 записів — результат тих самих восьми кроків для кожного байта."""
    table = []
    for byte in range(256):
        c = byte
        for _ in range(8):
            c = (c >> 1) ^ POLY if c & 1 else c >> 1
        table.append(c)
    return table

CRC_TABLE = build_table()

def crc16_table(data, crc=INIT):
    for byte in data:
        crc = (crc >> 8) ^ CRC_TABLE[(crc ^ byte) & 0xFF]
    return crc
