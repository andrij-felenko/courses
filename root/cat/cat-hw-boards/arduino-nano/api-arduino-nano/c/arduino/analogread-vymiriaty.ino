void setup() {
    Serial.begin(9600);
}

void loop() {
    int raw = analogRead(A0);            // 0..1023
    float volts = raw * 5.0 / 1023.0;    // назад у вольти
    Serial.print(raw);
    Serial.print(F("  ->  "));
    Serial.print(volts, 3);              // три знаки після коми
    Serial.println(F(" В"));
    delay(200);
}
