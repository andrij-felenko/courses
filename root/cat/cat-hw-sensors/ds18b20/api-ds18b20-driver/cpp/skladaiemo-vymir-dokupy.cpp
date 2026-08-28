// Прочитати температуру одного DS18B20 на шині (Skip ROM — коли давач один).
// Повертає true й кладе °C у *out; false — якщо давача немає або CRC не зійшлось.
bool ds18b20_read(float *out) {
  // --- Прогін 1: наказати виміряти ---
  if (!ow_reset()) return false;      // немає presence — немає давача
  ow_write_byte(0xCC);                // Skip ROM: «усі, слухайте» (давач один)
  ow_write_byte(0x44);                // Convert T: почати перетворення

  delay(750);                         // блокуюче чекання на 12 бітах (див. нижче)

  // --- Прогін 2: забрати результат ---
  if (!ow_reset()) return false;
  ow_write_byte(0xCC);                // Skip ROM знову
  ow_write_byte(0xBE);                // Read Scratchpad: віддай пам'ять

  uint8_t sp[9];
  for (uint8_t i = 0; i < 9; i++)     // забираємо всі 9 байтів
    sp[i] = ow_read_byte();

  if (ow_crc8(sp, 9) != 0)            // CRC над усіма 9 має дати 0
    return false;                     // не дало → читання зіпсоване, викидаємо

  // --- Декод: перші два байти — температура, 16-бітове доповняльне число ---
  int16_t raw = (int16_t)((sp[1] << 8) | sp[0]);   // старший байт sp[1], молодший sp[0]
  *out = raw * 0.0625f;               // молодший біт важить 2⁻⁴ = 0.0625 °C
  return true;
}
