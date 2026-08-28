void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000) { }

  pinMode(PIN_CLK, OUTPUT);
  pinMode(PIN_RST, OUTPUT);
  digitalWrite(PIN_RST, LOW);          // сеанс закритий, поки не почали

  // Пустити годинник, якщо стоїть (скинути CH). Час НЕ чіпаємо, якщо вже йде.
  ds_write_protect_off();
  ds_clock_start();
  ds_write(REG_WP, 0x80);

  // Виставити час ОДИН раз, якщо мікросхема свіжа. Розкоментуйте, прошийте,
  // тоді закоментуйте назад і прошийте вдруге — інакше час скидатиметься щоразу.
  // Clock init = { 30, 47, 10, 4, 7, 5, 26 };  // 10:47:30, 4 липня, чт(5), 2026
  // ds_set_time(init);
}

void loop() {
  Clock now;
  ds_read_burst(now);

  char buf[32];
  snprintf(buf, sizeof(buf), "20%02u-%02u-%02u %02u:%02u:%02u  (дн.тижня %u)",
           now.year, now.month, now.date,
           now.hour, now.min, now.sec, now.dow);
  Serial.println(buf);

  delay(1000);
}
