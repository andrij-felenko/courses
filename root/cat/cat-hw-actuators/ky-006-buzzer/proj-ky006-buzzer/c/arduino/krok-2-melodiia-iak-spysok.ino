struct Note { unsigned int freq; unsigned int dur; };  // частота Гц, тривалість мс

// ── Стан плеєра ──
const Note*   melody     = nullptr;  // на яку мелодію показуємо
uint16_t      melodyLen  = 0;        // скільки в ній нот
uint16_t      noteIndex  = 0;        // яку ноту гратимемо наступною
unsigned long phaseEndAt = 0;        // millis(), коли скінчиться поточна фаза
bool          playing    = false;
bool          inGap      = false;    // true = зараз мовчазна пауза між нотами

const uint16_t GAP_MS = 30;  // тривалість тиші між сусідніми нотами

// Запустити мелодію (не блокує). arr — масив нот, len — його довжина.
void playMelody(const Note* arr, uint16_t len) {
  melody     = arr;
  melodyLen  = len;
  noteIndex  = 0;
  playing    = true;
  inGap      = true;        // старт у фазі «пауза вже вичерпана» → перша нота піде одразу
  phaseEndAt = millis();    // не чекати: на найближчому витку візьмемо ноту 0
}

// Кликати на КОЖНОМУ витку loop().
void buzzerUpdate() {
  if (!playing) return;
  if (millis() < phaseEndAt) return;         // поточна фаза (нота чи пауза) ще триває

  if (inGap) {
    // Пауза скінчилась → завести чергову ноту.
    Note n = melody[noteIndex++];            // беремо ноту й зсуваємо індекс
    if (n.freq > 0) tone(PIN_BUZ, n.freq);   // REST (freq 0) — лишаємо в тиші
    inGap      = false;
    phaseEndAt = millis() + n.dur;           // нота звучить рівно свій dur
  } else {
    // Нота відзвучала → погасити й вставити РЕАЛЬНУ паузу.
    noTone(PIN_BUZ);
    if (noteIndex >= melodyLen) {            // нот більше немає — мелодія скінчилась
      playing = false;
      return;
    }
    inGap      = true;
    phaseEndAt = millis() + GAP_MS;          // ← ось вона, справжня тиша між нотами
  }
}
