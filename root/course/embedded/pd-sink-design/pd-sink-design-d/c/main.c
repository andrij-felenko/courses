// Таймер на 400 мс (із запасом до дедлайну 500 мс) — окреме переривання.
// Спрацьовує НЕЗАЛЕЖНО від того, чим зайнятий основний код.
volatile bool epr_active = false;

void TIM_EPR_IRQHandler(void) {
    tim_clear_flag(TIM_EPR);
    if (epr_active)
        pd_send_epr_keepalive();   // нагадати джерелу: я тут, тримай 48 В
}

// Коли контролер підтвердив вхід в EPR-режим — заводимо таймер:
void on_epr_entered(void) {
    epr_active = true;
    tim_start_periodic(TIM_EPR, 400 /*мс*/);   // 400 < 500 — маємо запас
}

// Будь-який відкат (Hard Reset, від'єднання, вихід з EPR) — гасимо таймер:
void on_fall_to_safe(void) {
    epr_active = false;
    tim_stop(TIM_EPR);
    disable_load();                // навантаження геть, як завжди
}
