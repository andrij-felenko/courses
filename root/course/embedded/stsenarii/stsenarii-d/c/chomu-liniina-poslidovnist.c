/* НАЇВНИЙ БЛОКУЮЧИЙ ПІДХІД — ДЖЕРЕЛО КАТАСТРОФ */
void prepare_start_sequence_blocking(void) {
    valve_open(VALVE_DRAIN);
    delay_ms(500);                        /* Зависання CPU на 500 мс */

    pump_set_power(PUMP_MAIN, 30);
    uint32_t t0 = get_system_ms();
    while (sensor_get_flow() < 4.0f) {    /* Блокуюче опитування датчика */
        if ((uint32_t)(get_system_ms() - t0) > 3000) {
            system_panic();               /* Аварійне скидання */
        }
        delay_ms(10);
    }

    valve_close(VALVE_DRAIN);
    pump_set_power(PUMP_MAIN, 80);
    while (sensor_get_pressure() < 3.5f) { /* Ще одне зависання до 4 секунд */
        delay_ms(10);
    }

    heater_enable(HEATER_PRIMARY);
}
