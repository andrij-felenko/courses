#include <stdint.h>

// Параметри мережі та імпульсу, мкс:
#define HALF_PERIOD_US  10000u   // півперіод 50 Гц; для 60 Гц ≈ 8333
#define PULSE_US          100u   // довжина імпульсу на затвор
#define GUARD_US          200u   // поля: не стріляти впритул до країв

// Апаратний шар плати (реалізується під конкретний МК):
extern void timer_start_oneshot_us(uint32_t us);  // одноразовий таймер → on_timer()
extern void gate_high(void);   // підняти лінію оптодрайвера затвора
extern void gate_low(void);    // опустити її
// Числове обернення кривої потужності: частка p∈[0,1] → кут α∈[0,π].
// Реалізацію див. у math-вставці (0 % → π, 100 % → 0).
extern float brightness_to_alpha(float p);

static uint16_t d_tab[101];         // таблиця затримок під шкалу 0…100, мкс
volatile uint8_t brightness = 0;    // лінійна ручка; пише цикл, читає ISR

static uint16_t clamp_u16(uint32_t v, uint16_t lo, uint16_t hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return (uint16_t)v;
}

// Підготовка (раз на старті): рівна шкала яскравості → нерівні затримки.
void dimmer_build_table(void) {
    const float pi = 3.14159265f;
    for (int b = 0; b <= 100; b++) {
        float alpha = brightness_to_alpha(b / 100.0f);         // кут запуску
        uint32_t d = (uint32_t)(alpha / pi * HALF_PERIOD_US);  // кут → час
        d_tab[b] = clamp_u16(d, GUARD_US, HALF_PERIOD_US - GUARD_US);
    }
}

// Дві фази одного таймера: спершу відлік затримки, потім утримання імпульсу.
typedef enum { PHASE_DELAY, PHASE_PULSE } phase_t;
static volatile phase_t phase;

// IRQ детектора нуля — точка відліку. КОРОТКО: лише запуск таймера.
void on_zero_cross(void) {
    if (brightness == 0) return;                // повний нуль — не стріляти
    phase = PHASE_DELAY;
    timer_start_oneshot_us(d_tab[brightness]);  // відлік від ЦЬОГО нуля
}

// IRQ таймера — обидві фази сходяться сюди, розрізняє їх phase.
void on_timer(void) {
    if (phase == PHASE_DELAY) {            // спливла затримка d — час стріляти
        gate_high();                       // імпульс на затвор
        phase = PHASE_PULSE;
        timer_start_oneshot_us(PULSE_US);  // таймер сам відміряє довжину імпульсу…
    } else {                               // спливла довжина імпульсу
        gate_low();                        // …і прибираємо, без блокувань у ISR
    }
}
