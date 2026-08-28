// ESP32, Arduino-core 3.x — апаратний PWM через LEDC.
const int ESC_PIN = 18;    // сигнальний дріт ESC
const int FREQ    = 50;    // 50 Гц — стандарт ESC
const int RES     = 14;    // розрядність лічильника (біт)
const int PERIOD_US = 20000; // 20 мс = період за 50 Гц

// Перевести ширину імпульсу (мкс) у число заповнення для цієї розрядності.
uint32_t usToDuty(uint32_t us) {
  return (uint32_t)((uint64_t)us * (1UL << RES) / PERIOD_US);
}

void setup() {
  ledcAttach(ESC_PIN, FREQ, RES);   // налаштувати й прив'язати вивід

  // ── ОЗБРОЄННЯ ────────────────────────────────────────────────────────
  ledcWrite(ESC_PIN, usToDuty(1000)); // мінімальний газ = «стоп»
  delay(3000);                        // дати ESC озброїтись
}

void loop() {
  // ── ПЛАВНИЙ РОЗГІН до половини газу ─────────────────────────────────
  for (int us = 1000; us <= 1500; us += 5) {
    ledcWrite(ESC_PIN, usToDuty(us));
    delay(20);
  }
  ledcWrite(ESC_PIN, usToDuty(1500));
  delay(3000);

  // ── ПЛАВНЕ ГАЛЬМУВАННЯ ──────────────────────────────────────────────
  for (int us = 1500; us >= 1000; us -= 5) {
    ledcWrite(ESC_PIN, usToDuty(us));
    delay(20);
  }
  ledcWrite(ESC_PIN, usToDuty(1000)); // повний стоп
  delay(3000);
}
