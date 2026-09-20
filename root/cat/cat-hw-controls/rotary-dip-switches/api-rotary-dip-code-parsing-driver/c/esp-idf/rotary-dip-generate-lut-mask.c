// Обчислення 8-бітної динамічної LUT-маски для вибірки активних бітів
static inline uint8_t rotary_dip_generate_lut_mask(uint8_t raw_bus, uint8_t bit_count, uint8_t active_mask) {
    uint8_t result = 0;
    uint8_t target_bit = 0;
    for (uint8_t i = 0; i < 8; i++) {
        if (active_mask & (1U << i)) {
            if (raw_bus & (1U << i)) {
                result |= (1U << target_bit);
            }
            target_bit++;
            if (target_bit >= bit_count) break;
        }
    }
    return result;
}
