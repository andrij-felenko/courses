static void tc_tick(port_t *p) {
    cc_seen_t cc = tcpc_cc_seen();
    uint32_t  held = now_ms() - p->t_enter;

    switch (p->state) {
    case TC_UNATTACHED:
        toggle_drp(p);
        // побачили ДЖЕРЕЛО (чужий Rp + жива VBUS) -> у бік стоку
        if (cc == CC_RP_PARTNER && tcpc_vbus_present())
            enter(p, TC_ATTACHWAIT_SNK);
        // побачили СТІК (чужий Rd) -> у бік джерела
        else if (cc == CC_RD_PARTNER)
            enter(p, TC_ATTACHWAIT_SRC);
        break;

    case TC_ATTACHWAIT_SNK:
        if (cc != CC_RP_PARTNER || !tcpc_vbus_present()) {
            enter(p, TC_UNATTACHED);            // брязкіт -> назад
        } else if (cc_stable_ms(p, cc) >= tCCDebounce_MS) {
            enter(p, p->try_src ? TC_TRY_SRC     // вподобання: спробувати джерелом
                                : TC_ATTACHED_SNK);
        }
        break;

    case TC_ATTACHWAIT_SRC:
        if (cc != CC_RD_PARTNER)
            enter(p, TC_UNATTACHED);
        else if (cc_stable_ms(p, cc) >= tCCDebounce_MS)
            enter(p, TC_ATTACHED_SRC);
        break;

    case TC_TRY_SRC:
        // партнер став стоком (стабільний Rd) -> ми виграли джерело
        if (cc == CC_RD_PARTNER && cc_stable_ms(p, cc) >= tTryCCDeb_MS)
            enter(p, TC_ATTACHED_SRC);
        // час вийшов, а Rd не з'явився -> поступаємось
        else if (held >= tDRPTry_MS)
            enter(p, TC_TRYWAIT_SNK);
        break;

    case TC_TRYWAIT_SNK:
        if (cc == CC_OPEN && cc_stable_ms(p, cc) >= tPDDebounce_MS)
            enter(p, TC_UNATTACHED);
        else if (tcpc_vbus_present() && held >= tCCDebounce_MS)
            enter(p, TC_ATTACHED_SNK);
        break;

    case TC_ATTACHED_SNK:
        if (!tcpc_vbus_present() && cc_stable_ms(p, cc) >= tPDDebounce_MS)
            enter(p, TC_UNATTACHED);            // джерело зникло
        else
            prswap_tick(p);                     // може йти обмін ролі
        break;

    case TC_ATTACHED_SRC:
        if (tcpc_fault_oc())
            enter(p, TC_ERROR_RECOVERY);        // коротке/перевантаження виходу
        else if (cc == CC_OPEN && cc_stable_ms(p, cc) >= tPDDebounce_MS)
            enter(p, TC_UNATTACHED);            // партнер від'єднався
        else
            prswap_tick(p);
        break;

    case TC_ERROR_RECOVERY:
        if (held >= tErrRecovery_MS)
            enter(p, TC_UNATTACHED);
        break;
    }
}
