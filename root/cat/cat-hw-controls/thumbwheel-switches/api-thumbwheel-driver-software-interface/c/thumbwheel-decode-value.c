// Конвертація тетрад у ціле число з перевіркою помилок
thumbwheel_status_t thumbwheel_decode_value(thumbwheel_driver_t *drv, uint16_t *out_value) {
    uint16_t result = 0;
    uint16_t multiplier = 1;
    
    for (uint8_t i = 0; i < drv->config.decades_count; i++) {
        uint8_t bcd = drv->nibbles[i];
        
        // Перевірка на невалідний BCD-код (10...15)
        if (bcd > 9) {
            return THUMBWHEEL_ERR_INVALID_BCD;
        }
        
        result += bcd * multiplier;
        multiplier *= 10;
    }
    
    drv->validated_value = result;
    *out_value = result;
    return THUMBWHEEL_OK;
}
