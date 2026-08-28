const uint8_t LASER = 9;   // пін S модуля -> цифровий вивід 9

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
