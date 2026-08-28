SYNC = 0xAA

# CRC-8, поліном 0x07 (x⁸+x²+x+1) — без таблиці, для наочності
def crc8(data: bytes) -> int:
    crc = 0x00
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc
