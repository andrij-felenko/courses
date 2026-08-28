// Частоти нот у герцах (рівномірний стрій; A4 = 440 Гц як опорна)
#define NOTE_C4  262
#define NOTE_D4  294
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_G4  392
#define NOTE_A4  440
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_REST  0            // 0 Гц = пауза (noTone)

const uint8_t BUZ = 8;

void setup() {
  pinMode(BUZ, OUTPUT);
}

// Одна нота: увімкнути частоту, витримати, вимкнути
void playNote(uint16_t freq, uint16_t ms) {
  if (freq == NOTE_REST) noTone(BUZ);   // пауза — просто тиша
  else                   tone(BUZ, freq);
  delay(ms);
  noTone(BUZ);
}

void loop() {
  playNote(NOTE_C4, 200);
  playNote(NOTE_E4, 200);
  playNote(NOTE_G4, 200);
  playNote(NOTE_C5, 400);
  delay(2000);
}
