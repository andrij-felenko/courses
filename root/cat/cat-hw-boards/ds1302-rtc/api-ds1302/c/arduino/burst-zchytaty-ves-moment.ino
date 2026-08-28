// Прочитати весь календар одним «burst»-сеансом — цілісний зріз часу.
void ds_read_burst(Clock& c) {
  digitalWrite(PIN_RST, LOW);
  digitalWrite(PIN_CLK, LOW);
  pinMode(PIN_DAT, OUTPUT);
  digitalWrite(PIN_RST, HIGH);

  shift_out_byte(0xBF);            // clock-burst READ (0xBE — запис пачкою)
  pinMode(PIN_DAT, INPUT);        // віддаємо лінію мікросхемі на всі 8 байтів

  uint8_t raw[8];
  for (uint8_t i = 0; i < 8; i++) raw[i] = shift_in_byte();

  digitalWrite(PIN_RST, LOW);

  // Порядок регістрів у пачці фіксований даташитом:
  // 0:сек 1:хв 2:год 3:число 4:місяць 5:день-тижня 6:рік 7:захист
  c.sec   = bcd_to_dec(raw[0] & 0x7F);   // маскуємо CH (біт7)
  c.min   = bcd_to_dec(raw[1] & 0x7F);
  c.hour  = bcd_to_dec(raw[2] & 0x3F);   // 24-год: беремо біти 0..5
  c.date  = bcd_to_dec(raw[3] & 0x3F);
  c.month = bcd_to_dec(raw[4] & 0x1F);
  c.dow   = bcd_to_dec(raw[5] & 0x07);
  c.year  = bcd_to_dec(raw[6]);
  // raw[7] — регістр захисту, у зрізі часу не потрібен
}
