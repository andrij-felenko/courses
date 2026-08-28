// Прочитати конкретний давач за його 64-бітним ROM-кодом (8 байтів).
bool ds18b20_read_addr(const uint8_t rom[8], float *out) {
  // Прогін 1: адресуємо саме цей давач і наказуємо виміряти.
  if (!ow_reset()) return false;
  ow_write_byte(0x55);                // Match ROM: «слухає лише той, чий код далі»
  for (uint8_t i = 0; i < 8; i++)     // вимовляємо 64-бітний код, байт за байтом
    ow_write_byte(rom[i]);
  ow_write_byte(0x44);                // Convert T — тільки адресований почне рахувати

  delay(750);

  // Прогін 2: знову адресуємо його ж і забираємо scratchpad.
  if (!ow_reset()) return false;
  ow_write_byte(0x55);
  for (uint8_t i = 0; i < 8; i++)
    ow_write_byte(rom[i]);
  ow_write_byte(0xBE);                // Read Scratchpad

  uint8_t sp[9];
  for (uint8_t i = 0; i < 9; i++)
    sp[i] = ow_read_byte();
  if (ow_crc8(sp, 9) != 0) return false;

  int16_t raw = (int16_t)((sp[1] << 8) | sp[0]);
  *out = raw * 0.0625f;
  return true;
}
