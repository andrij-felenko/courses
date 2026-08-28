typedef struct { uint16_t freq; uint16_t dur; } Note;   // частота Гц, тривалість мс

// ── Стан плеєра ──
static const Note *melody     = NULL;   // на яку мелодію показуємо
static uint16_t    melodyLen  = 0;      // скільки в ній нот
static uint16_t    noteIndex  = 0;      // яку ноту гратимемо наступною
static uint32_t    phaseEndAt = 0;      // HAL_GetTick(), кінець поточної фази
static bool        playing    = false;
static bool        inGap      = false;  // true = зараз мовчазна пауза між нотами

#define GAP_MS  30U   // тривалість тиші між сусідніми нотами

// Запустити мелодію (не блокує). arr — масив нот, len — його довжина.
void playMelody(const Note *arr, uint16_t len)
{
    melody     = arr;
    melodyLen  = len;
    noteIndex  = 0;
    playing    = true;
    inGap      = true;             // фаза «пауза вже вичерпана»
    phaseEndAt = HAL_GetTick();    // перша нота піде на найближчому витку
}

// Кликати на КОЖНОМУ витку while(1).
void buzzerUpdate(void)
{
    if (!playing) return;
    uint32_t now = HAL_GetTick();
    if (now < phaseEndAt) return;       // фаза (нота чи пауза) ще триває

    if (inGap) {
        // Пауза скінчилась → завести чергову ноту.
        Note n = melody[noteIndex++];
        if (n.freq > 0) buzzerTone(n.freq);   // REST (freq 0) — лишаємо в тиші
        inGap      = false;
        phaseEndAt = now + n.dur;
    } else {
        // Нота відзвучала → погасити й вставити РЕАЛЬНУ паузу.
        buzzerOff();
        if (noteIndex >= melodyLen) {         // нот більше немає
            playing = false;
            return;
        }
        inGap      = true;
        phaseEndAt = now + GAP_MS;            // ← справжня тиша між нотами
    }
}
