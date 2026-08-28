template <periph_tag Tag>
inline void trace_clock_event(std::uint8_t event_type, std::uint8_t ref_cnt) noexcept {
    #if defined(ENABLE_ITM_CLOCK_TRACING)
    if ((itm->tcr & itm_tcr_itmen_msk) && (itm->ter & (1UL << 0))) {
        const auto timestamp = static_cast<std::uint32_t>(dwt->cyccnt & 0xFFFF);
        const auto packet = (timestamp << 16) | (static_cast<std::uint32_t>(Tag) << 8) | 
                            ((static_cast<std::uint32_t>(event_type) & 0xF) << 4) | (ref_cnt & 0xF);
        itm->port[0].u32 = packet;
    }
    #else
    (void)event_type; (void)ref_cnt;
    #endif
}
