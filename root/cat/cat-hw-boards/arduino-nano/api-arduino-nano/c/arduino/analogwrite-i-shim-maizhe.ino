const uint8_t PIN_LED = 9;   // ~D9 — має апаратний ШІМ

void setup() {
    pinMode(PIN_LED, OUTPUT);
}

void loop() {
    // плавне «дихання»: яскравість вгору й вниз
    for (int d = 0; d <= 255; d++) { analogWrite(PIN_LED, d); delay(5); }
    for (int d = 255; d >= 0; d--) { analogWrite(PIN_LED, d); delay(5); }
}
