static void enter(port_t *p, tc_state_t s) {
    p->state = s;
    p->t_enter = now_ms();
    switch (s) {
    case TC_UNATTACHED:
        vbus_apply(DIR_OFF);
        tcpc_vconn(false);
        p->show_rp = false;
        tcpc_set_cc(CC_PULL_RD);       // стартуємо як стік — безпечно
        p->t_toggle = now_ms();
        break;
    case TC_ATTACHWAIT_SNK:
        tcpc_set_cc(CC_PULL_RD);
        break;
    case TC_ATTACHWAIT_SRC:
        tcpc_set_cc(CC_PULL_RP);
        break;
    case TC_ATTACHED_SNK:
        tcpc_set_cc(CC_PULL_RD);
        vbus_apply(DIR_SINK);          // споживаємо чужу напругу
        break;
    case TC_ATTACHED_SRC:
        tcpc_set_cc(CC_PULL_RP);
        vbus_apply(DIR_SOURCE);        // жену свої 5 В
        tcpc_vconn(true);              // живимо e-marker кабелю
        break;
    case TC_TRY_SRC:
        vbus_apply(DIR_OFF);
        tcpc_set_cc(CC_PULL_RP);       // наполягаємо: я джерело
        break;
    case TC_TRYWAIT_SNK:
        tcpc_set_cc(CC_PULL_RD);       // поступились: пробуємо стоком
        break;
    case TC_ERROR_RECOVERY:
        vbus_apply(DIR_OFF);
        tcpc_vconn(false);
        tcpc_set_cc(CC_PULL_OPEN);     // повний скид на tErrRecovery
        break;
    }
}
