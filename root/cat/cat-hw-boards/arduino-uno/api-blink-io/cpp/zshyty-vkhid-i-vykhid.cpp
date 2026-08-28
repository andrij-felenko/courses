const uint8_t PIN_POT = A0;   // потенціометр
const uint8_t PIN_LED = 9;    // світлодіод на ~9

void setup() {
    pinMode(PIN_LED, OUTPUT);
}

void loop() {
    int raw = analogRead(PIN_POT);          // 0…1023 (10 біт)
    int duty = map(raw, 0, 1023, 0, 255);   // масштабуємо в 0…255 (8 біт)
    analogWrite(PIN_LED, duty);             // яскравість слідує за повзунком
}
