// Читає найстарший байт другої половини серійного номера (SNB3),
// що кодує модель чипа. Повертає true й кладе байт у *id_out при успіху.
bool si7021_read_model_id(uint8_t *id_out) {
  // -- Друга половина серійного номера: команда 0xFC 0xC9 --
  Wire.beginTransmission(GY21_ADDR);
  Wire.write(0xFC);
  Wire.write(0xC9);
  if (Wire.endTransmission() != 0) return false;

  // Пристрій віддає 6 байтів: SNB3, SNB2, CRC, SNB1, SNB0, CRC.
  // Нам потрібен найперший (SNB3) — він і є ідентифікатор моделі.
  if (Wire.requestFrom((int)GY21_ADDR, 6) != 6) return false;
  uint8_t snb3 = Wire.read();      // <- ідентифікатор моделі
  // решту байтів дочитуємо, щоб не лишати «хвіст» у буфері шини:
  while (Wire.available()) Wire.read();

  *id_out = snb3;
  return true;
}

// Зручна обгортка: назвати модель словами.
const char* gy21_model_name() {
  uint8_t id;
  if (!si7021_read_model_id(&id)) return "HTU21D або сумісний (не Si70xx)";
  switch (id) {
    case 0x15: return "Si7021";
    case 0x14: return "Si7020";
    case 0x0D: return "Si7013";
    case 0x00:
    case 0xFF: return "Si70xx (інженерний зразок)";
    default:   return "невідомий Si70xx";
  }
}
