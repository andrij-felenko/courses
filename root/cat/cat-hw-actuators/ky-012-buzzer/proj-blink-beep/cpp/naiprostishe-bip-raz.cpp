const uint8_t BUZZER = 8;          // S модуля на цифровому виході

void setup() {
  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);       // старт із тиші — відомий початковий стан
}

// Один біп заданої довжини (мс). Блокуючий — годиться для найпростіших місць.
void beep(unsigned int ms) {
  digitalWrite(BUZZER, HIGH);      // одиниця → транзистор відкрився → пищить
  delay(ms);
  digitalWrite(BUZZER, LOW);       // забрали → тиша
}

void loop() {
  beep(80);                        // короткий «тик»
  delay(2000);                     // раз на дві секунди
}
