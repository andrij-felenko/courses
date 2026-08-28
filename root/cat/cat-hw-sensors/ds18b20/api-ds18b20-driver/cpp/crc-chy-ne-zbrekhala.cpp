// Dallas/Maxim CRC-8, поліном X8+X5+X4+1 (відображений вигляд → 0x8C).
uint8_t ow_crc8(const uint8_t *data, uint8_t len) {
  uint8_t crc = 0;
  for (uint8_t i = 0; i < len; i++) {
    uint8_t b = data[i];
    for (uint8_t j = 0; j < 8; j++) {
      uint8_t mix = (crc ^ b) & 1;    // чи різняться молодші біти
      crc >>= 1;
      if (mix) crc ^= 0x8C;           // якщо так — підмішуємо поліном
      b >>= 1;
    }
  }
  return crc;                         // 0, якщо порахувати над усіма 9 байтами
}
