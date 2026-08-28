/* Хеш рядка "ADC ch=%u timeout after %u ms" обчислюється препроцесором */
#define TOKEN_ADC_TIMEOUT 0x8F3A2B1C

void log_adc_timeout(uint8_t ch, uint32_t ms) {
    uint8_t payload[5];
    payload[0] = ch;
    payload[1] = (uint8_t)(ms & 0xFF);
    payload[2] = (uint8_t)((ms >> 8) & 0xFF);
    payload[3] = (uint8_t)((ms >> 16) & 0xFF);
    payload[4] = (uint8_t)((ms >> 24) & 0xFF);
    LOG_EMIT(LOG_LEVEL_WARN, 1, TOKEN_ADC_TIMEOUT, payload, sizeof(payload));
}
