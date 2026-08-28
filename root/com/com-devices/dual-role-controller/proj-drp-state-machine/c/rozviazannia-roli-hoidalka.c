static void toggle_drp(port_t *p) {
    uint32_t dt  = now_ms() - p->t_toggle;
    uint32_t rp_win = (uint32_t)tDRP_MS * dcSRC_DRP_PCT / 100;   // фаза Rp
    uint32_t win = p->show_rp ? rp_win : (tDRP_MS - rp_win);     // фаза Rd
    if (dt >= win) {
        p->show_rp = !p->show_rp;
        tcpc_set_cc(p->show_rp ? CC_PULL_RP : CC_PULL_RD);
        p->t_toggle = now_ms();
    }
}

// Скільки мілісекунд CC тримає поточне значення (для дебаунсу країв)
static uint32_t cc_stable_ms(port_t *p, cc_seen_t cc) {
    if (cc != p->cc_last) { p->cc_last = cc; p->t_cc_edge = now_ms(); }
    return now_ms() - p->t_cc_edge;
}
