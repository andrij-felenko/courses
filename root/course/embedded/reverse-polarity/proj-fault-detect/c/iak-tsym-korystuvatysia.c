// Пороги під 5-вольтову шину (усе в мВ). Один конфіг = одна плата.
static const pm_config_t CFG_5V = {
    .div_num = 3, .div_den = 1,     // дільник 3:1 → 5 В на нозі стає ~1.67 В
    .vref_mv = 3300, .adc_full = 4095,

    .v_nominal_mv = 5000,           // очікуємо 5.0 В
    .v_dead_mv    = 500,            // < 0.5 В — мертва шина
    .v_sag_trip_mv= 4500,           // < 4.5 В — оголосити просад
    .v_sag_heal_mv= 4750,           // > 4.75 В — просад знято (зазор 250 мВ)
    .diode_drop_mv= 600,            // body-діод ~0.6 В
    .diode_tol_mv = 200,            // вікно ±0.2 В навколо 5.0−0.6 = 4.4 В

    .confirm_dead = 3,              // мертву/body-діод — за 3 відліки
    .confirm_sag  = 10,             // просад терпимо довше (кидки струму — норма)
    .confirm_ok   = 30,             // назад у норму — за 30 добрих поспіль
};

static pm_channel_t vin_mon;

// Платформний шматок: прочитати канал АЦП шини (сирий код).
// Вибірку тримаємо ПОВІЛЬНОЮ: дільник високоомний, швидкий відлік занизить.
static uint16_t read_vin_adc(void) {
    return adc_read_raw_slow(ADC_CH_VIN);   // довгий SamplingTime
}

// Реакції плати.
static void save_critical(void)      { fram_store_context(); }   // швидкий запис
static void switch_load(bool on)     { gpio_write(LOAD_EN, on); }// ключ навантаження
static void report_class(pm_class_t c){
    switch (c) {
        case PM_OK:        led_set(LED_GREEN);  log_line("power OK");            break;
        case PM_SAG:       led_blink(LED_AMBER);log_line("power SAG");           break;
        case PM_DEAD:      led_set(LED_RED);    log_line("power DEAD (fuse?)");  break;
        case PM_BODYDIODE: led_blink(LED_RED);  log_line("REVERSE? FET body-diode");break;
    }
}

static const pm_actions_t ACT = {
    .save_state = save_critical,
    .set_load   = switch_load,
    .on_class   = report_class,
};

void power_mon_setup(void) {
    pm_init(&vin_mon, &CFG_5V);
}

void power_mon_loop(void) {
    pm_poll(&vin_mon, read_vin_adc, &ACT);   // раз на 1–5 мс (таймер/головний цикл)
    // ... решта роботи пристрою ...
}
