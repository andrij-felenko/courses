static coulomb_counter_t cc;

void app_measure_one_cycle(void)
{
    // 0) при холодному старті — один раз відкалібрувати нуль:
    //    знеструмити навантаження й усереднити 512 вибірок.
    //    (offset потім варто зберегти в NVS і не повторювати щоразу)
    // cc_calibrate_zero(&cc, board_read_current_adc, 512);

    // 1) активна фаза: будимося таймером кожні 100 мкс, семплимо АЦП.
    //    Тут — передача радіо тривалістю ~300 мс.
    for (int i = 0; i < 3000; i++) {          // 3000 × 100 мкс = 300 мс
        uint16_t code = board_read_current_adc();
        cc_step_active(&cc, code, 100);       // dt = 100 мкс
        timer_wait_us(100);
    }

    // 2) глибокий сон: АЦП вимкнено, струм сну відомий з даташита (10 мкА).
    //    Замість семплу — один доданок за весь сон.
    uint64_t t_sleep = 600ull * 1000000ull - 300000ull;   // 600 с − 0.3 с, у мкс
    board_enter_deep_sleep(t_sleep);          // прокидається за t_sleep
    cc_add_sleep(&cc, 10000, t_sleep);        // I_сон = 10 мкА = 10 000 нА

    // 3) читаємо підсумок циклу
    int32_t i_avg_nA = cc_average_nA(&cc);    // середній струм за цикл, нА
    int32_t q_uAh    = cc_charge_mAh_milli(&cc);  // накопичено, мкА·год
    log_report(i_avg_nA, q_uAh, cc.saturated);
}
