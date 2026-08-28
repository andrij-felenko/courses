// CC-фаза: тримати струм заряду I_TARGET, підкручуючи напругу PPS по 20 мВ.
// Викликається періодично (раз на ~200 мс), поки комірка не дійшла коліна.
void pps_cc_step(void) {
    int i_ma = batt_current_ma();          // виміряний струм у комірку
    int v_mv = pps_req_mv;                 // поточна запитана напруга

    if (i_ma < I_TARGET_MA - 50)           // струму замало —
        v_mv += 20;                        //   підняти на один крок PPS
    else if (i_ma > I_TARGET_MA + 50)      // забагато —
        v_mv -= 20;                        //   опустити на крок

    if (batt_voltage_mv() >= V_CV_MV)      // комірка дійшла коліна —
        charger_enter_cv();                //   далі веде CV-цикл

    v_mv = clamp(v_mv, APDO_MIN_MV, APDO_MAX_MV);
    pps_request(v_mv, I_TARGET_MA);        // новий APDO-запит — він же keep-alive
    pps_req_mv = v_mv;
}
