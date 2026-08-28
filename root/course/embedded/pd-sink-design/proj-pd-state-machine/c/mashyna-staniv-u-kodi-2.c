// Переривання (таймер, PHY, інтерфейс CC) НЕ чіпають st напряму —
// вони лише кладуть подію в чергу. Розбирає її ОДИН цикл, тож стан
// живе в єдиному контексті й гонок за st не буває.
typedef enum { EV_ATTACH, EV_DETACH, EV_HARD_RESET, EV_MSG, EV_TIMEOUT } ev_t;
typedef struct { ev_t type; msg_t msg; const pdo_t *pdo; int n; } event_t;

static queue_t pd_ev;   // невелика черга подій sink-задачі

void TIM_PD_IRQHandler(void) {              // вийшов дедлайн стану очікування
    tim_clear_flag(TIM_PD);
    queue_push(&pd_ev, (event_t){ .type = EV_TIMEOUT });
}

void sink_task(void) {                      // ЄДИНЕ місце, де крутиться машина
    event_t e;
    for (;;) {
        if (!queue_pop(&pd_ev, &e)) { wait_for_irq(); continue; }  // сон, не busy-wait
        switch (e.type) {
        case EV_ATTACH:     on_attach();                    break;
        case EV_MSG:        on_message(e.msg, e.pdo, e.n);   break;
        case EV_TIMEOUT:    fall_to_safe("таймаут");         break;
        case EV_DETACH:     fall_to_safe("від'єднання");     break;
        case EV_HARD_RESET: fall_to_safe("hard reset");      break;
        }
    }
}
