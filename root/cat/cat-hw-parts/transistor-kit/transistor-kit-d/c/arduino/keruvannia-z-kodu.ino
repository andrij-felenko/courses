const uint8_t MOTOR_PIN = 5;   // GPIO → Rb → база NPN-ключа

void setup() {
  pinMode(MOTOR_PIN, OUTPUT);
  digitalWrite(MOTOR_PIN, LOW); // старт: транзистор закритий, мотор стоїть
}

void loop() {
  digitalWrite(MOTOR_PIN, HIGH);  // «1» → база відкрита → мотор крутиться
  delay(2000);
  digitalWrite(MOTOR_PIN, LOW);   // «0» → база закрита → мотор стоїть
  delay(2000);
}
