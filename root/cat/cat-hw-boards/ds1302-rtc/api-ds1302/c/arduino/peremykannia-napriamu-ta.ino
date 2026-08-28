// ── Один регістр: запис ──
void ds_write(uint8_t cmd, uint8_t data) {
  digitalWrite(PIN_RST, LOW);
  digitalWrite(PIN_CLK, LOW);
  pinMode(PIN_DAT, OUTPUT);
  digitalWrite(PIN_RST, HIGH);      // почали сеанс

  shift_out_byte(cmd);              // командний байт (біт0 = 0, запис)
  shift_out_byte(data);             // байт даних

  digitalWrite(PIN_RST, LOW);       // завершили — дані зафіксовано
}

// ── Один регістр: читання ──
uint8_t ds_read(uint8_t cmd) {
  digitalWrite(PIN_RST, LOW);
  digitalWrite(PIN_CLK, LOW);
  pinMode(PIN_DAT, OUTPUT);
  digitalWrite(PIN_RST, HIGH);      // почали сеанс

  shift_out_byte(cmd | 0x01);       // командний байт із бітом ЧИТАННЯ (біт0=1)
  pinMode(PIN_DAT, INPUT);          // ← ключове: віддаємо лінію мікросхемі
  uint8_t data = shift_in_byte();   // забрали байт

  digitalWrite(PIN_RST, LOW);       // завершили сеанс
  return data;
}
