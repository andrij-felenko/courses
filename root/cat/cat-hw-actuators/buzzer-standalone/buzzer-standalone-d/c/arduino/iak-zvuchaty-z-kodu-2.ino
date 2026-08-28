const uint8_t BUZ = 8;          // вивід із пасивним зумером

// Частоти нот у герцах (рівномірний стрій, октава 4-5)
#define NOTE_C5  523
#define NOTE_E5  659
#define NOTE_G5  784

void setup() {
  pinMode(BUZ, OUTPUT);
}

void playNote(uint16_t freq, uint16_t ms) {
  tone(BUZ, freq);               // жене меандр цієї частоти — диск бринить нотою
  delay(ms);                     // тримаємо ноту
  noTone(BUZ);                   // зупиняємо меандр — тиша
}

void loop() {
  playNote(NOTE_C5, 200);        // до
  playNote(NOTE_E5, 200);        // мі
  playNote(NOTE_G5, 300);        // соль — простенький акорд «по черзі»
  delay(1500);
}
