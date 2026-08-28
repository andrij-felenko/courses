const uint8_t AO = A0;              // аналоговий вихід давача на A0

void setup() {
    Serial.begin(9600);
}

void loop() {
    int v = analogRead(AO);         // 0..1023 на Uno; менше = мокріше
    Serial.println(v);              // ← дивимося сухе й мокре значення
    delay(300);
}
