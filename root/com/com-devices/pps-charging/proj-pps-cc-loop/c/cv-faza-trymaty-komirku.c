static void enter_cv(void) { g_state = ST_CV; }

// CV: тримати комірку на V_CELL_TARGET_MV, стежити за спадом струму до термінації.
void pps_cv_step(void) {
    int i_ma  = batt_current_ma();
    int vc_mv = batt_voltage_mv();

    // Феедфорвард: запит = ціль + I·R. Струм спадає → I·R тане → запит сам іде вниз.
    g_vreq_mv = clamp_to_apdo_v(port_for_cell(V_CELL_TARGET_MV, i_ma));

    // Дрібний трим за ВИМІРЯНОЮ коміркою — бо R у формулі не ідеальний.
    if (vc_mv > V_CELL_TARGET_MV + 10)
        g_vreq_mv = clamp_to_apdo_v(g_vreq_mv - PPS_VSTEP_MV);   // перелили — прибрати крок
    else if (vc_mv < V_CELL_TARGET_MV - 10)
        g_vreq_mv = clamp_to_apdo_v(g_vreq_mv + PPS_VSTEP_MV);   // недолили — додати крок

    // Стелю лишаємо на CC-рівні: у CV вона не активна, але хай стоїть дахом.
    g_ilim_ma = clamp_to_apdo_i(g_i_charge_ma);

    if (i_ma <= I_TERM_MA) {          // струм упав до порога — заряд завершено
        g_state = ST_DONE;
        pps_request(g_vreq_mv, g_ilim_ma);   // останній keep-alive перед завершенням
        charger_finished();
        return;
    }
    pps_request(g_vreq_mv, g_ilim_ma);   // корекція + keep-alive
}
