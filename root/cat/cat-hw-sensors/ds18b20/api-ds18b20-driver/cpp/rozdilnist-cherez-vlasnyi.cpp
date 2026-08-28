// Виставити роздільність: 9, 10, 11 або 12 біт.
void ds18b20_set_resolution(uint8_t bits) {
  uint8_t cfg;
  switch (bits) {
    case 9:  cfg = 0x1F; break;       // R1R0 = 00
    case 10: cfg = 0x3F; break;       // R1R0 = 01
    case 11: cfg = 0x5F; break;       // R1R0 = 10
    default: cfg = 0x7F; break;       // 12 біт, R1R0 = 11 (за замовчуванням)
  }
  ow_reset();
  ow_write_byte(0xCC);                // Skip ROM (або Match ROM для конкретного)
  ow_write_byte(0x4E);                // Write Scratchpad
  ow_write_byte(0x00);                // TH — верхній поріг тривоги (тут не використ.)
  ow_write_byte(0x00);                // TL — нижній поріг тривоги
  ow_write_byte(cfg);                 // регістр налаштувань → роздільність
}
