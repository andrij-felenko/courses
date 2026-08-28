# CRC-8, поліном x⁸+x⁵+x⁴+1 (0x31), початкове значення 0x00.
# Рахуємо над байтами `data`; для GY-21 це 2 байти даних виміру.
def si7021_crc8(data):
    crc = 0x00                             # початкове значення регістра
    for byte in data:
        crc ^= byte                        # внести черговий байт
        for _ in range(8):
            if crc & 0x80:                  # старший біт = 1?
                crc = ((crc << 1) ^ 0x31) & 0xFF  # зсув + XOR з поліномом
            else:
                crc = (crc << 1) & 0xFF     # інакше просто зсув
    return crc
