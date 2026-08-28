// C = t / (k·R), де k = ln2 ≈ 0.693 при порозі V₀/2.
float measure_capacitance(float R_ohms) {
    static uint32_t discharge_us = 200000;   // щедрий старт на перший цикл

    pinMode(PIN_DRIVE, OUTPUT);
    digitalWrite(PIN_DRIVE, LOW);            // 1. розряд крізь R
    uint32_t d0 = micros();
    while (micros() - d0 < discharge_us) { /* тримаємо, поки не сяде до ~0 */ }

    uint32_t t0 = micros();
    digitalWrite(PIN_DRIVE, HIGH);           // 2. старт заряду й таймера воднораз

    while (digitalRead(PIN_SENSE) == LOW) { } // 3. чекаємо перетину порога V₀/2
    uint32_t t_us = micros() - t0;           //    тривалість заряду ≈ 0.69·τ

    discharge_us = 8 * t_us;                 // наступний розряд: 8·0.69τ ≈ 5.5τ ≥ 5τ
    return (t_us * 1e-6f) / (0.693f * R_ohms); // 4. ділимо на k·R → фаради
}
