/* ============================================================================
   krok-3-en-load-switch.ino — Керування піном EN та ключем навантаження
   ========================================================================== */

const uint8_t PIN_MT3608_EN = 4;
const uint8_t PIN_LOAD_GATE = 5;

void setBoostEnabled(bool enabled) {
    if (enabled) {
        digitalWrite(PIN_MT3608_EN, HIGH);
        delay(15);
        digitalWrite(PIN_LOAD_GATE, LOW); // Увімкнути P-MOSFET
    } else {
        digitalWrite(PIN_LOAD_GATE, HIGH); // Вимкнути навантаження (повні 0 В)
        digitalWrite(PIN_MT3608_EN, LOW);  // Зупинити перетворювач
    }
}

void setup() {
    pinMode(PIN_MT3608_EN, OUTPUT);
    pinMode(PIN_LOAD_GATE, OUTPUT);
    setBoostEnabled(false);
}

void loop() {
    delay(5000);
    setBoostEnabled(true);
    delay(5000);
    setBoostEnabled(false);
}
