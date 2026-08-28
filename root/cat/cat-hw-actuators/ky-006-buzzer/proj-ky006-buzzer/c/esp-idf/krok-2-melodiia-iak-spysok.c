typedef struct { uint16_t freq; uint16_t dur; } note_t;  // частота Гц, тривалість мс

// ── Стан плеєра ──
static const note_t *melody     = NULL;   // на яку мелодію показуємо
static uint16_t      melodyLen  = 0;      // скільки в ній нот
static uint16_t      noteIndex  = 0;      // яку ноту гратимемо наступною
static int64_t       phaseEndAt = 0;      // кінець поточної фази, мкс
static bool          playing    = false;
static bool          inGap      = false;  // true = зараз мовчазна пауза між нотами

#define GAP_US  (30 * 1000)   // 30 мс тиші між сусідніми нотами

// Запустити мелодію (не блокує). arr — масив нот, len — його довжина.
void playMelody(const note_t *arr, uint16_t len)
{
    melody     = arr;
    melodyLen  = len;
    noteIndex  = 0;
    playing    = true;
    inGap      = true;                     // фаза «пауза вже вичерпана»
    phaseEndAt = esp_timer_get_time();     // перша нота піде на найближчому витку
}

void buzzerUpdate(void)
{
    if (!playing) return;
    int64_t now = esp_timer_get_time();
    if (now < phaseEndAt) return;          // фаза (нота чи пауза) ще триває

    if (inGap) {
        // Пауза скінчилась → завести чергову ноту.
        note_t n = melody[noteIndex++];
        if (n.freq > 0) buzzerTone(n.freq);   // REST (freq 0) — лишаємо в тиші
        inGap      = false;
        phaseEndAt = now + (int64_t)n.dur * 1000;
    } else {
        // Нота відзвучала → погасити й вставити РЕАЛЬНУ паузу.
        buzzerOff();
        if (noteIndex >= melodyLen) {         // нот більше немає
            playing = false;
            return;
        }
        inGap      = true;
        phaseEndAt = now + GAP_US;            // ← справжня тиша між нотами
    }
}
