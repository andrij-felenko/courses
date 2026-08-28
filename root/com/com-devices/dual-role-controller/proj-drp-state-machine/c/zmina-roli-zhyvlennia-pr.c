static bool accept_swap(port_t *p);   // політика: чи згодні мінятись зараз

// Прийшло PD-повідомлення (кличеться з приймача PD)
void prswap_on_msg(port_t *p, int msg) {
    switch (msg) {
    case PD_PR_SWAP:                              // партнер просить обмін
        if (accept_swap(p)) { pd_send(PD_ACCEPT); begin_swap(p); }
        else                  pd_send(PD_REJECT);
        break;
    case PD_ACCEPT:                               // наш запит прийнято
        if (p->swap == SWAP_WAIT_ACCEPT) begin_swap(p);
        break;
    case PD_REJECT:                               // партнер відмовив
        if (p->swap == SWAP_WAIT_ACCEPT) p->swap = SWAP_IDLE;  // лишаємось як є
        break;
    case PD_PS_RDY:                               // старе джерело: «я вимкнувся»
        if (p->swap == SWAP_WAIT_PSRDY) {         // ми новий -> час давати VBUS
            p->swap   = SWAP_SRC_ON;
            p->t_swap = now_ms();
        }
        break;
    }
}

static void begin_swap(port_t *p) {
    if (p->state == TC_ATTACHED_SRC) {            // ми джерело -> станемо стоком
        p->swap = SWAP_SRC_OFF;
        tcpc_src_switch(false);                   // геть ключ-джерело
        tcpc_discharge(true);                     // активно зціджуємо VBUS
    } else {                                      // ми стік -> станемо джерелом
        p->swap = SWAP_WAIT_PSRDY;                // чекаємо, поки той вимкнеться
    }
    p->t_swap = now_ms();
}
