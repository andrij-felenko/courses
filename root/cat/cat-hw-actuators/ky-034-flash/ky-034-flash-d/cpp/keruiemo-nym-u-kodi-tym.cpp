const uint8_t PIN_LED = 8;      // S модуля на цифровому виході

void setup() {
  pinMode(PIN_LED, OUTPUT);
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_LED, HIGH);   // подаємо живлення — модуль світиться (свій колір)
    delay(500);
    digitalWrite(PIN_LED, LOW);    // прибираємо живлення — модуль згас
    delay(500);
  }
}

void loop() {
  // далі нічого: блимнули тричі на старті й затихли
}
