#define LOOP_HZ   400
#define DT_US     (1000000UL / LOOP_HZ)   // 2500 мкс = 2.5 мс
#define DT_S      (1.0f / LOOP_HZ)        // 0.0025 с — крок для ПІД

static uint32_t next_tick;                // строк наступного такту, мкс

void control_loop_init(void) {
    estimator_init();
    pid_init();
    next_tick = micros() + DT_US;
}

void control_loop_run(void) {
    for (;;) {
        // 1. дочекатися РІВНОГО строку (не «через 2.5 мс від кінця роботи»)
        while ((int32_t)(micros() - next_tick) < 0) { /* короткий простій */ }
        next_tick += DT_US;               // наступний строк — від попереднього

        control_tick();                   // увесь контур за один прохід

        // 2. сторож: чи ми взагалі вклалися в Δt?
        if ((int32_t)(micros() - next_tick) > 0) {
            stats.overruns++;             // такт не вліз — це тривога, не дрібниця
        }
    }
}
