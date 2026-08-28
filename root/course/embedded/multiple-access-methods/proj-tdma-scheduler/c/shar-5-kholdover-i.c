typedef enum { ST_SEARCH, ST_SYNCED, ST_HOLDOVER } sched_state_t;
static sched_state_t g_state = ST_SEARCH;

#define HOLDOVER_LIMIT_US   15000000u    // 15 с — межа довіри власному годиннику
#define MARK_PERIOD_US      FRAME_US     // позначку чекаємо раз на кадр

// Викликається регулярно (раз на вікно з таймера) — рухає машину станів.
void scheduler_step(void) {
    uint64_t now      = now_us();
    uint64_t age      = now - g_last_mark_us;   // скільки минуло від останньої позначки

    switch (g_state) {
    case ST_SEARCH:
        // тільки слухаємо; перехід у SYNCED робить on_time_mark() ззовні
        radio_listen();
        break;

    case ST_SYNCED:
        if (age > MARK_PERIOD_US + GUARD_US) {   // позначку пропустили
            g_state = ST_HOLDOVER;               // ще тримаємось, але насторожі
        } else {
            run_slot_logic(now);                 // нормальна робота: рахуємо вікна
        }
        break;

    case ST_HOLDOVER:
        if (age > HOLDOVER_LIMIT_US) {           // тиша надто довго — більше не віримо собі
            g_synced = false;
            g_state  = ST_SEARCH;                // скидаємо все, шукаємо позначку заново
            radio_listen();
        } else {
            run_slot_logic(now);                 // поки в межах довіри — працюємо як є
        }
        break;
    }
}

// Повернення з холдовера у синхрон робить on_time_mark(): свіжа позначка → g_synced.
// scheduler_step() побачить свіжий g_last_mark_us і на наступному кроці буде в ST_SYNCED.
