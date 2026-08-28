void hipot_tick(hipot_t *h) {          // виклик кожні 1 мс
    // ── Аварійні умови — найперше, у будь-якому стані ──
    bool live = hv_is_live();
    if (live && enclosure_open())                 abort_test(h, "кожух відчинено");
    else if (live && !(button_l() && button_r())) abort_test(h, "відпущено кнопку");
    else if (g_trip)                              abort_test(h, "тригер: поріг або дуга");

    switch (h->state) {
    case ST_IDLE:
        hv_off(); bleed_off();
        g_level_armed = g_arc_armed = false;
        if (two_hand_ok() && !enclosure_open())
            enter(h, ST_GROUND_BOND);
        break;

    case ST_GROUND_BOND:                        // Клас I: 25 А, R < 0.1 Ом
        if (ground_bond_ohms() > 0.10f) abort_test(h, "заземл. звʼязок > 0.1 Ом");
        else if (h->t_ms > 500)         enter(h, ST_INSUL_RES);
        break;

    case ST_INSUL_RES:                          // 500 В=, R має бути > 10 МОм
        if (insul_res_megohm() < 10.0f) abort_test(h, "опір ізоляції < 10 МОм");
        else if (h->t_ms > 1000) {
            ramp_setup(h, volts_to_code(2121), 2000);
            g_arc_armed = true;                 // дугу стежимо вже з наростання
            enter(h, ST_HIPOT_RAMP);
        }
        break;

    case ST_HIPOT_RAMP:                         // наростання: активний ЛИШЕ детектор дуги
        h->dac_code += h->dac_step;
        if (h->dac_code >= h->dac_target) {
            h->dac_code = h->dac_target;
            g_level_armed = true;               // у витримці вмикаємо й абсолютний поріг
            enter(h, ST_HIPOT_DWELL);
        }
        dac_write(h->dac_code);
        break;

    case ST_HIPOT_DWELL:                        // витримка: поріг + дуга
        if (h->t_ms > DWELL_MS) { h->verdict = V_PASS; enter(h, ST_DISCHARGE); }
        break;

    case ST_DISCHARGE:                          // спільний вузол: і успіх, і ABORT
        hv_off(); bleed_on();
        g_level_armed = g_arc_armed = false;
        if (hv_meas_volts() < 50) {             // ВИМІР, не таймер
            bleed_off();
            enter(h, h->verdict == V_FAIL ? ST_FAIL : ST_PASS);
        } else if (h->t_ms > DISCHARGE_TIMEOUT_MS) {
            latch_fault("розряд не завершився"); // баласт відгорів — станцію в стоп
        }
        break;

    case ST_PASS:
    case ST_FAIL:
        log_result(h);
        enter(h, ST_IDLE);
        break;
    }
    h->t_ms++;
}
