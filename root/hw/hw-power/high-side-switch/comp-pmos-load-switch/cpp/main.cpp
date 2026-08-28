// P-ключ навантаження: NPN-перекладач інвертує всередині себе,
// але для МК логіка пряма — HIGH вмикає стрічку.
constexpr uint8_t PIN_LOAD = 5;   // → Rb → база NPN

void setup() {
    pinMode(PIN_LOAD, OUTPUT);
    digitalWrite(PIN_LOAD, LOW);   // старт вимкнено: NPN off, R1 тримає затвор вгорі
}

void loop() {
    digitalWrite(PIN_LOAD, HIGH);  // увімкнути: NPN тягне затвор вниз, плавний пуск через C
    delay(2000);
    digitalWrite(PIN_LOAD, LOW);   // вимкнути: затвор повертається до +12 В
    delay(2000);
}
