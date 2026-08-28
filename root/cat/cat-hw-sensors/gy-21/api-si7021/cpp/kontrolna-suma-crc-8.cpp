// CRC-8, поліном x⁸+x⁵+x⁴+1 (0x31), початкове значення 0x00.
// Рахуємо над `len` байтами; для GY-21 len = 2 (два байти даних виміру).
uint8_t si7021_crc8(const uint8_t *data, uint8_t len) {
  uint8_t crc = 0x00;                      // початкове значення регістра
  for (uint8_t i = 0; i < len; i++) {
    crc ^= data[i];                        // внести черговий байт
    for (uint8_t bit = 0; bit < 8; bit++) {
      if (crc & 0x80)                       // старший біт = 1?
        crc = (uint8_t)((crc << 1) ^ 0x31); //   зсув + XOR з поліномом
      else
        crc = (uint8_t)(crc << 1);          //   інакше просто зсув
    }
  }
  return crc;
}
