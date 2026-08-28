// Порахувати частоту LCO для заданої ємності tune (0..15).
// Повертає виміряну частоту в Гц (уже помножену на дільник).
uint32_t measureLco(uint8_t tune) {
  lightning.setTuningCaps(tune * 8);        // 0, 8, 16 … 120 пФ
  lightning.setIRQOutputSource(3);          // вивести LCO на пін IRQ
  delay(2);                                 // дати сигналу устоятися

  // Рахуємо фронти на піні IRQ за вікно 100 мс.
  const uint32_t windowMs = 100;
  uint32_t edges = 0;
  int last = digitalRead(IRQ_PIN);
  uint32_t t0 = millis();
  while (millis() - t0 < windowMs) {
    int now = digitalRead(IRQ_PIN);
    if (now == HIGH && last == LOW) edges++; // порахувати фронт ↑
    last = now;
  }
  lightning.setIRQOutputSource(0);          // ПРИБРАТИ LCO з піна!

  // Дільник за замовчуванням — 16 (LCO_FDIV). Частота антени:
  //   f = фронти / час · дільник
  //   edges за 0.1 с → множимо на 10, щоб дістати за секунду, тоді ·16
  return edges * (1000UL / windowMs) * 16UL;
}

// Перебрати 16 ємностей, знайти ту, де частота найближча до 500 кГц.
uint8_t findBestCaps() {
  const int32_t target = 500000;            // 500 кГц
  uint8_t best = 0;
  int32_t bestErr = INT32_MAX;
  for (uint8_t tune = 0; tune < 16; tune++) {
    int32_t f = (int32_t)measureLco(tune);
    int32_t err = f > target ? f - target : target - f;   // |f − 500 кГц|
    Serial.print("tune="); Serial.print(tune);
    Serial.print("  f="); Serial.print(f);
    Serial.print("  промах="); Serial.println(err);
    if (err < bestErr) { bestErr = err; best = tune; }
  }
  Serial.print("Найкраща ємність: tune="); Serial.print(best);
  Serial.print(" ("); Serial.print(best * 8); Serial.println(" пФ)");
  return best;
}
