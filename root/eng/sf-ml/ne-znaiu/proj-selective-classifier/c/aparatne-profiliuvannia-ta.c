// Ініціалізація DWT лічильника тактів на ARM Cortex-M
void profile_selective_filter_c(const float* logits, size_t n, const selective_config_t* cfg) {
    selective_output_t res;
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    DWT->CYCCNT = 0;

    uint32_t t_start = DWT->CYCCNT;
    selective_classify_process(cfg, logits, n, &res);
    uint32_t t_cycles = DWT->CYCCNT - t_start;
    (void)t_cycles;
}
