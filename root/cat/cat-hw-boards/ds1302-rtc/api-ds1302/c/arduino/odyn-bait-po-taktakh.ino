// Виставити один байт у мікросхему (біти 0..7, молодший уперед).
// DAT має бути вже переведений на ВИХІД.
void shift_out_byte(uint8_t v) {
  for (uint8_t i = 0; i < 8; i++) {
    digitalWrite(PIN_DAT, (v >> i) & 0x01);   // виставили біт i
    digitalWrite(PIN_CLK, HIGH);              // ↑ фронт: мікросхема зчитала
    delayMicroseconds(1);
    digitalWrite(PIN_CLK, LOW);               // ↓ готуємось до наступного біта
    delayMicroseconds(1);
  }
}

// Забрати один байт із мікросхеми (біти 0..7, молодший уперед).
// DAT має бути вже переведений на ВХІД.
uint8_t shift_in_byte() {
  uint8_t v = 0;
  for (uint8_t i = 0; i < 8; i++) {
    // Мікросхема міняє біт по спадному фронту; читаємо ПІСЛЯ нього.
    if (digitalRead(PIN_DAT)) v |= (1 << i);
    digitalWrite(PIN_CLK, HIGH);              // такт для наступного біта
    delayMicroseconds(1);
    digitalWrite(PIN_CLK, LOW);               // ↓ фронт: мікросхема виставила новий біт
    delayMicroseconds(1);
  }
  return v;
}
