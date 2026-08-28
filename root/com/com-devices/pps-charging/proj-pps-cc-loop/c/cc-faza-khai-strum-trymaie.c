// CC: тримати струм комірки на g_i_charge_ma. Кличеться періодично, ~кожні 150 мс.
void pps_cc_step(void) {
    int vc_mv = batt_voltage_mv();   // струм тут навмисно НЕ міряємо: його тримає джерело в CL

    if (vc_mv >= V_CELL_TARGET_MV) { enter_cv(); return; }   // дійшли коліна → у CV

    // Стеля струму = сам цільовий струм. У режимі CL джерело САМЕ тримає рівно її —
    // ось і захист від перельоту: хай напруга смикнеться, струм вище стелі не піде.
    g_ilim_ma = clamp_to_apdo_i(g_i_charge_ma);

    // Запит напруги: досить високий, щоб джерело лишалось у CL і віддавало стелю.
    // port_for_cell додає падіння I·R у кабелі; CC_HEADROOM — запас, щоб не випасти з CL.
    g_vreq_mv = clamp_to_apdo_v(port_for_cell(vc_mv, g_i_charge_ma) + CC_HEADROOM_MV);

    if (!pps_source_in_cl())          // джерело НЕ в CL → струму недобір: тиснемо вище
        g_vreq_mv = clamp_to_apdo_v(g_vreq_mv + PPS_VSTEP_MV);

    pps_request(g_vreq_mv, g_ilim_ma);   // новий запит: і корекція, і keep-alive
}
