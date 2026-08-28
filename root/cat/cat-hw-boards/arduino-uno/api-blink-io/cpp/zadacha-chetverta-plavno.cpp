const uint8_t PIN_LED = 9;    // світлодіод на ~9 (через резистор!)

void setup() {
    pinMode(PIN_LED, OUTPUT);
}

void loop() {
    // Плавно розгоряємось: 0 → 255
    for (int duty = 0; duty <= 255; duty++) {
        analogWrite(PIN_LED, duty);
        delay(5);
    }
    // ...і гаснемо назад
    for (int duty = 255; duty >= 0; duty--) {
        analogWrite(PIN_LED, duty);
        delay(5);
    }
}
