// ── Готові сигнали-квитанції ──

// Успіх: дві висхідні ноти, бадьоро. «ді-дінь!»
const Note SND_OK[] = {
  {NOTE_G4, 90}, {NOTE_C5, 140},
};

// Помилка: дві спадні низькі ноти, глухо. «дон-дон».
const Note SND_ERROR[] = {
  {NOTE_E4, 160}, {NOTE_C4, 260},
};

// Попередження: три однакові короткі писки, наполегливо. «пік-пік-пік».
// Явних пауз не треба — плеєр сам розділить однакові ноти своєю фазою GAP_MS.
const Note SND_WARN[] = {
  {NOTE_A5, 80}, {NOTE_A5, 80}, {NOTE_A5, 80},
};

// Зручні обгортки — читаються за змістом, а не за нотами.
#define N(arr) (arr), (sizeof(arr) / sizeof((arr)[0]))
void soundOk()    { playMelody(N(SND_OK));    }
void soundError() { playMelody(N(SND_ERROR)); }
void soundWarn()  { playMelody(N(SND_WARN));  }
