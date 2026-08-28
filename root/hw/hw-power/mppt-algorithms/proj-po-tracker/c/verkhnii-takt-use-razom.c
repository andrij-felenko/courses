extern uint16_t adc_batt_vmv(void);   // напруга батареї (свої канали, ті ж усереднення)
extern uint16_t adc_batt_ima(void);   // струм заряду

// Викликати РІВНО раз на 1 мс (з таймера).
void tracker_tick(void) {
    if (!soft_done) { soft_start_tick(); return; }   // 1) спершу м'який старт

    uint16_t vb = adc_batt_vmv();
    uint16_t ib = adc_batt_ima();
    supervisor_update(vb, ib);                        // 2) хто крутить D?

    if (mode != MODE_MPPT) {                          // 3) кермо в регулятора заряду
        if (mode == MODE_CV) regulate_cv(vb);
        else                 regulate_cc(ib);
        phase = PH_SETTLE; ph_ms = 0;                 //   скинути фазу P&O на потім
        return;
    }

    // 4) MODE_MPPT: фазовий цикл «влягання → вимір → рішення»
    if (phase == PH_SETTLE) {
        if (++ph_ms >= SETTLE_MS) {                   // влягання скінчилось
            phase = PH_MEASURE; ph_ms = 0;
            meas_acc_p = 0; meas_n = 0;
        }
        return;                                       // МОВЧКИ чекаємо, не міряємо
    }

    // PH_MEASURE: збираємо усереднену потужність за вікно
    meas_t m = measure_panel();
    meas_acc_p += m.puw;
    ++meas_n;
    if (++ph_ms >= MEAS_MS) {                         // вікно заповнене — рішення
        meas_t avg = m;
        avg.puw = meas_acc_p / (int32_t)meas_n;       // середнє за вікно
        po_decide(&avg);                              // збурити D у (можливо) новому напрямі
        phase = PH_SETTLE; ph_ms = 0;                 // і знову чекати влягання
    }
}
