const uint8_t PIN_BUZ = 8;

// частоти нот у герцах
const int C4 = 262, D4 = 294, E4 = 330, F4 = 349, G4 = 392;

// мелодія: пари {частота, тривалість у мс}. 0 = пауза (тиша)
const int melody[][2] = {
  {E4, 300}, {E4, 300}, {F4, 300}, {G4, 300},
  {G4, 300}, {F4, 300}, {E4, 300}, {D4, 300}, {C4, 500},
};

void setup() {
  pinMode(PIN_BUZ, OUTPUT);
  for (auto &note : melody) {
    int freq = note[0], dur = note[1];
    if (freq > 0)
      tone(PIN_BUZ, freq, dur);   // грати ноту freq протягом dur мс
    else
      noTone(PIN_BUZ);            // freq==0 → пауза
    // між нотами — маленький проміжок тиші, щоб ноти не зливались
    delay(dur + 40);
    noTone(PIN_BUZ);
  }
}

void loop() {}
