/* ============================================================================
   krok-1-dummy-load-control.ino — Керування баластом B0505S
   ========================================================================== */

const uint8_t PIN_DUMMY_LOAD_EN = 8;
const uint8_t PIN_ISO_PWR_EN    = 9;

void setup() {
    Serial.begin(115200);
    pinMode(PIN_DUMMY_LOAD_EN, OUTPUT);
    pinMode(PIN_ISO_PWR_EN, OUTPUT);

    // Вмикаємо баластний резистор перед подачею напруги
    digitalWrite(PIN_DUMMY_LOAD_EN, HIGH);
    delay(5);
    digitalWrite(PIN_ISO_PWR_EN, HIGH);

    Serial.println(F("[B0505S] Ізольоване живлення запущено з баластом 220 Ом"));
}

void loop() {
    // Демонстрація динамічного керування баластом
}
