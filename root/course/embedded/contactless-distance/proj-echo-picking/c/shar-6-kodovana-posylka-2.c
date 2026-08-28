// Пошук відлуння за КОРЕЛЯЦІЄЮ (замість простого порога амплітуди).
static uint32_t find_echo_coded(uint32_t t0, int32_t corr_thr) {
    int16_t win[TPL_LEN] = {0};
    int     head = 0;
    for (;;) {
        uint32_t t = micros() - t0;
        if (t >= TIMEOUT_US) return 0;

        // зсунути вікно й покласти свіжий відлік (з грубим відніманням середини шкали)
        win[head] = (int16_t)((int)adc_read() - 2048);
        head = (head + 1) % TPL_LEN;

        if (t > BLANK_US && abs(chirp_match(win)) > corr_thr)
            return t;                              // збіг із нашим чирпом → це наше відлуння
    }
}
