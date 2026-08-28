// Глобальний контекст регулятора (пам'ять між викликами).
static regulator_t g_reg = { .state = ST_STOP, .charge_ma = 0, .heater_on = false };

// Викликати періодично (раз на ~100 мс).
void thermal_tick(void) {
    uint16_t codes[N_SENSORS];

    // 1) Зчитати кожен давач: медіана кількох вимірів проти викидів.
    for (int s = 0; s < N_SENSORS; s++) {
        uint16_t samp[5];
        for (int k = 0; k < 5; k++)
            samp[k] = adc_read(NTC_CH[s]);     // апаратне читання каналу
        codes[s] = adc_median(samp, 5);
    }

    // 2) Прокрутити машину станів (вона сама зробить шари 1–3 усередині).
    regulator_step(&g_reg, codes);

    // 3) Застосувати рішення до заліза.
    charger_set_current_ma(g_reg.charge_ma);   // задати ліміт зарядці
    heater_set(g_reg.heater_on);               // увімкнути/вимкнути нагрівач
}
