const int POT = 34;            // ADC1-ніжка (Wi-Fi-safe)

void setup() {
  Serial.begin(115200);
  // вхід; виклик opinionated — ADC-ніжки читаються і без pinMode
}

void loop() {
  int raw = analogRead(POT);              // 0…4095 — «номер щабля»
  float v  = raw * 3.3f / 4095.0f;        // назад у вольти: код · опорна / макс. код
  int pct  = map(raw, 0, 4095, 0, 100);   // поворот у відсотках
  Serial.printf("raw=%4d  v=%.2f  pos=%d%%\n", raw, v, pct);
  delay(100);
}
