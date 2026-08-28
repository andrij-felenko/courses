const uint8_t PIN_POT = A0;   // повзунок потенціометра на A0

void setup() {
    Serial.begin(9600);       // відкриваємо канал у монітор порту
}

void loop() {
    int raw = analogRead(PIN_POT);        // 0…1023
    float volts = raw * 5.0 / 1023.0;     // назад у вольти
    Serial.print("raw=");
    Serial.print(raw);
    Serial.print("  U=");
    Serial.print(volts, 2);               // 2 знаки після коми
    Serial.println(" V");
    delay(200);
}
