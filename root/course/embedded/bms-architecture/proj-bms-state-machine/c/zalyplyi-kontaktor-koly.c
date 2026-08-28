#define CONTACTOR_RESPOND_MS  30u   // стільки даємо контактору на спрацювання

static bool main_cmd = false;        // що ми НАКАЗАЛИ головному востаннє
static uint32_t main_cmd_t = 0;      // коли наказали

// Обгортка над командою головному: запам'ятовуємо намір і час.
static void cmd_main(bool on) {
    main_cmd = on;
    main_cmd_t = now_ms();
    contactor_main(on);
}

// Звірити намір із реальністю (aux). Викликати в ON і при розмиканні.
static void watch_stuck_contactor(uint32_t t)
{
    if (t - main_cmd_t < CONTACTOR_RESPOND_MS) return;  // ще не встиг — чекаємо

    bool real = aux_main_closed();

    if (main_cmd && !real) {
        // Наказали замкнути — не замкнувся. Коло не зібралось як слід.
        enter_fault(FAULT_CONTACTOR_STUCK);
    }
    else if (!main_cmd && real) {
        // Наказали розімкнути — ЗВАРЕНИЙ. Рвемо коло іншим контактором!
        contactor_neg(false);         // останній шанс розірвати коло
        enter_fault(FAULT_CONTACTOR_STUCK);
    }
}
