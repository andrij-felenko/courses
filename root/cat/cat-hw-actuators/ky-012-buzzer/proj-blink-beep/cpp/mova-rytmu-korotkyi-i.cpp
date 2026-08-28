const uint8_t BUZZER = 8;

void setup() {
  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);
}

void beep(unsigned int ms) {
  digitalWrite(BUZZER, HIGH);
  delay(ms);
  digitalWrite(BUZZER, LOW);
}

// N однакових біпів по on мс зі паузою gap мс між ними.
void beepN(uint8_t n, unsigned int on, unsigned int gap) {
  for (uint8_t i = 0; i < n; i++) {
    beep(on);
    if (i < n - 1) delay(gap);     // паузу ставимо МІЖ біпами, не після останнього
  }
}

// Іменовані сигнали — це просто зручні назви для конкретних ритмів.
void signalReady() { beep(120); }                 // готово: один короткий
void signalError() { beepN(3, 60, 80); }          // помилка: три швидкі
void signalAttention() { beep(600); }             // увага: один довгий
void alarm(uint8_t times) { beepN(times, 400, 200); } // тривога: довгі з паузами

void loop() {
  signalReady();
  delay(1500);
  signalError();
  delay(1500);
  alarm(3);
  delay(3000);
}
