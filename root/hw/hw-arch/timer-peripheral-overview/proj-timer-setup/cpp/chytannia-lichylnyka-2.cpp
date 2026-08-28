uint32_t micros_since_start() {
    uint32_t hi, cnt, pending;

    do {
        hi      = ms_ticks.load(std::memory_order_relaxed);
        cnt     = TIM3->CNT;
        pending = TIM3->SR & TIM_SR_UIF;
    } while (hi != ms_ticks.load(std::memory_order_relaxed));

    if (pending && cnt < (arr_val / 2u)) {
        hi++;
    }

    return hi * 1000u + cnt;
}
