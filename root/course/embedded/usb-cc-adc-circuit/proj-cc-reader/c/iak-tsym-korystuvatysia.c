// Платформний шматок: прочитати CC1/CC2 у мВ. Тут — усереднення вже НЕ робимо
// (його робить кільцевий буфер у модулі), але вибірку тримаємо ПОВІЛЬНОЮ —
// дільник CC високоомний, швидкий відлік дасть занижене число.
static uint16_t board_read_cc_mv(cc_line_t line) {
    uint32_t ch = (line == CC_LINE_1) ? ADC_CH_CC1 : ADC_CH_CC2;
    return adc_read_mv_slow(ch);    // довгий SamplingTime / великий sample div
}

static void on_cc_event(cc_event_t ev, cc_level_t lvl, void *user) {
    switch (ev) {
        case CC_EV_ATTACHED:
        case CC_EV_LEVEL:
            set_input_current_limit(lvl == CC_3A0 ? 3000 :
                                    lvl == CC_1A5 ? 1500 :
                                    lvl == CC_DEFAULT ? 500 : 0);
            load_enable(lvl != CC_NONE);   // навантаження — лише за дійсним рівнем
            break;
        case CC_EV_DETACHED:
            load_enable(false);            // кабель зник — гасимо негайно
            set_input_current_limit(0);
            break;
    }
}

void app_main_setup(void) {
    cc_reader_cfg_t cfg = {
        .read_mv  = board_read_cc_mv,
        .on_event = on_cc_event,
        .user     = NULL,
    };
    cc_reader_init(&cfg);
}

void app_main_loop(void) {
    cc_reader_poll();          // раз на кожен оберт циклу (або по таймеру ~1–5 мс)
    // ... решта роботи пристрою ...
}
