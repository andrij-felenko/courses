// N-фазний зсув: один такт ділимо на N рівних інтервалів.
// TIMER_TOP — значення лічильника за повний такт (=1/f).
#define N_PHASES   4
#define TIMER_TOP  1000u   // тактів таймера на один період комутації

// Поріг старту фази i: рівномірний зсув на 360°/N.
static inline uint16_t phase_start(uint8_t i) {
    // i-та фаза починає свій такт на (i * TIMER_TOP / N)
    return (uint16_t)((uint32_t)i * TIMER_TOP / N_PHASES);
}

void setup_phase_offsets(void) {
    for (uint8_t i = 0; i < N_PHASES; i++) {
        // кожній фазі — власний зсув фази ШІМ у її таймері/каналі
        pwm_set_phase(i, phase_start(i));   // 0, 250, 500, 750 тактів
    }
}
