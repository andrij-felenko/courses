/* ============================================================================
   krok-2-current-estimator.ino — Оцінка струму дроселя MT3608
   ========================================================================== */

bool isCurrentWithinSafetyLimit(float vin_v, float vout_v, float i_load_a) {
    if (vout_v <= vin_v) return true;
    float d = 1.0f - (vin_v / vout_v);
    float i_in_a = i_load_a / ((1.0f - d) * 0.88f);
    return i_in_a <= 1.8f; // Ліміт 1.8 А
}

void setup() {
    Serial.begin(115200);
}

void loop() {
    // Перевірка режиму: 3.7 В -> 12 В при навантаженні 0.4 А
    bool ok = isCurrentWithinSafetyLimit(3.7f, 12.0f, 0.4f);
    if (!ok) {
        Serial.println(F("⚠ Небезпечне перевантаження дроселя MT3608!"));
    }
    delay(1000);
}
