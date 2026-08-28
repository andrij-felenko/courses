const uint8_t LASER = 4;   // пін S модуля -> GPIO4 (ESP32) або D4 (Arduino)

void setup() {
    pinMode(LASER, OUTPUT);
    digitalWrite(LASER, LOW);   // старт з вимкненим променем — гарна звичка
}

void loop() {
    digitalWrite(LASER, HIGH);  // промінь увімкнено
    delay(1000);
    digitalWrite(LASER, LOW);   // промінь вимкнено
    delay(1000);
}
