/* БЕЗПЕЧНО: Час роботи повністю незалежний від позиції та наявності розбіжностей */
bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    volatile uint8_t diff = 0;
    
    for (size_t i = 0; i < len; ++i) {
        diff |= (uint8_t)(a[i] ^ b[i]);
    }
    
    return diff == 0;
}
