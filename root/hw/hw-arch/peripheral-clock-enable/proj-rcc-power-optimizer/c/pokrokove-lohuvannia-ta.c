static inline void clock_trace_event(periph_id_t id, uint8_t event_type, uint8_t ref_cnt) {
    #if defined(ENABLE_ITM_CLOCK_TRACING)
    // Перевірка готовності каналу ITM Channel 0
    if ((ITM->TCR & ITM_TCR_ITMENA_Msk) && (ITM->TER & (1UL << 0))) {
        uint32_t timestamp = (uint32_t)(DWT->CYCCNT & 0xFFFF);
        uint32_t packet = (timestamp << 16) | ((uint32_t)id << 8) | ((uint32_t)(event_type & 0xF) << 4) | (ref_cnt & 0xF);
        ITM->PORT[0].u32 = packet;
    }
    #else
    (void)id; (void)event_type; (void)ref_cnt;
    #endif
}
