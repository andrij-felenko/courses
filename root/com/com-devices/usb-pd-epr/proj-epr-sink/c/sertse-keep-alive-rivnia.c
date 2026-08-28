// ── Серцебиття keep-alive: рівня сторожового таймера ────────────────
// Бюджет за стандартом: слати не рідше ніж раз на tSinkEPRKeepAlive = 500 мс;
// джерело, не почувши нічого ~1 с, вважає це збоєм і скидає нас на 5 В.
// Тому б'ємось удвічі частіше — раз на 250 мс: навіть один пропущений
// імпульс (колізія, зайнята шина) ще влазить у бюджет із запасом.
#define KA_PERIOD_MS   250
#define KA_MISS_LIMIT  2       // два поспіль без ACK — самі падаємо в безпечне

static volatile uint8_t g_ka_misses = 0;

// Апаратний таймер зводимо на 250 мс і чіпляємо на нього обробник нижче.
void epr_keepalive_start(void) {
    g_ka_misses = 0;
    hw_timer_start(TIMER_KEEPALIVE, KA_PERIOD_MS);   // періодичний, з ISR
}

// ISR: спрацьовує строго кожні 250 мс — НАВІТЬ якщо головний цикл підвис.
void TIMER_KEEPALIVE_isr(void) {
    hw_timer_clear_flag(TIMER_KEEPALIVE);
    if (g_state != ST_EPR_ACTIVE) return;      // не в EPR — серцю нема чого битись

    if (g_ka_misses >= KA_MISS_LIMIT) {        // серцебиття вже фактично зникло
        epr_fallback_to_spr();                 // випереджаємо джерело: самі рвемо 48 В
        return;
    }
    pd_send_epr_keepalive();                    // «я живий, тримай напругу»
    g_ka_misses++;                              // рахуємо як пропуск, доки не прийде ACK
}

// PD-стек кличе це, коли на наш keep-alive прийшов EPR_KeepAlive_Ack.
void on_epr_keepalive_ack(void) {
    g_ka_misses = 0;                            // джерело відповіло — лічильник у нуль
}
