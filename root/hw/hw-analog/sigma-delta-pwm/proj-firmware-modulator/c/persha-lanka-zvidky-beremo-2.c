#define PHASE_BITS    24u                       // ширина фазового акумулятора
#define PHASE_MAX     (1uL << PHASE_BITS)        // повний оберт фази

static uint32_t phase_acc;                       // поточна фаза (накопичується)
static uint32_t phase_inc;                       // крок фази за такт → задає тон

// Перерахунок кроку фази під бажану частоту тону (Гц) і такт ISR (Гц).
// f_тону = f_такт · phase_inc / 2^PHASE_BITS  →  phase_inc = f_тону · 2^PHASE_BITS / f_такт
void set_tone_hz(uint32_t tone_hz, uint32_t isr_hz)
{
    phase_inc = (uint32_t)(((uint64_t)tone_hz << PHASE_BITS) / isr_hz);
}

// Один крок генератора: повернути миттєвий рівень синуса 0..255.
static inline uint8_t next_sine_level(void)
{
    phase_acc += phase_inc;                                  // крутимо фазу
    uint8_t idx = (uint8_t)(phase_acc >> (PHASE_BITS - 8));  // старші 8 бітів → індекс таблиці
    return sine_tab[idx];
}
