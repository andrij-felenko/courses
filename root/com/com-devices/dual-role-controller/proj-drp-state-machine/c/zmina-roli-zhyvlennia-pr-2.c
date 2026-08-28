static void prswap_tick(port_t *p) {
    uint32_t dt = now_ms() - p->t_swap;
    switch (p->swap) {
    case SWAP_IDLE:
        break;

    case SWAP_WAIT_ACCEPT:
        if (dt >= tSenderResponse_MS)
            p->swap = SWAP_IDLE;             // Accept не прийшов -> лишаємось як є
        break;

    case SWAP_SRC_OFF:                       // ми гасимо своє джерело
        if (tcpc_vbus_mv() <= VSAFE0V_MV) {
            tcpc_discharge(false);
            pd_send(PD_PS_RDY);              // «я вимкнувся, шина в нулі»
            p->swap = SWAP_IDLE;
            enter(p, TC_ATTACHED_SNK);        // тепер ми стік
        } else if (dt >= tSrcTransition_MS + 20) {
            enter(p, TC_ERROR_RECOVERY);      // не впали в нуль -> жорсткий скид
        }
        break;

    case SWAP_WAIT_PSRDY:                     // ми чекаємо, поки той вимкнеться
        if (dt >= tPSSourceOff_MS)
            enter(p, TC_ERROR_RECOVERY);      // PS_RDY не прийшов -> партнер завис
        break;

    case SWAP_SRC_ON:                         // ми піднімаємо нове джерело
        if (dt < tSwapSourceStart_MS)
            break;                            // коротка пауза перед подачею
        vbus_apply(DIR_SOURCE);
        if (tcpc_vbus_mv() >= VSAFE5V_MV) {
            pd_send(PD_PS_RDY);              // «я джерело, тримаю vSafe5V»
            p->swap = SWAP_IDLE;
            enter(p, TC_ATTACHED_SRC);        // тепер ми джерело
        } else if (dt >= tPSSourceOn_MS) {
            enter(p, TC_ERROR_RECOVERY);      // не піднялись вчасно -> скид
        }
        break;
    }
}
