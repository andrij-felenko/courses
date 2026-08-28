/* Високопродуктивний потоковий декодер UTF-8 на C99 */
uint32_t utf8_decode_next(const uint8_t **p_src, const uint8_t *src_end) {
    if (!p_src || !*p_src || *p_src >= src_end) return 0xFFFD; /* U+FFFD REPLACEMENT CHARACTER */
    
    const uint8_t *s = *p_src;
    uint8_t b0 = *s++;
    
    if (b0 < 0x80) {
        *p_src = s;
        return b0;
    }
    
    uint32_t cp = 0;
    size_t needed = 0;
    
    if ((b0 & 0xE0) == 0xC0) {
        cp = b0 & 0x1F;
        needed = 1;
        if (cp < 0x02) return 0xFFFD; /* Заборона надлишкового кодування (Overlong) */
    } else if ((b0 & 0xF0) == 0xE0) {
        cp = b0 & 0x0F;
        needed = 2;
    } else if ((b0 & 0xF8) == 0xF0) {
        cp = b0 & 0x07;
        needed = 3;
        if (cp > 0x04) return 0xFFFD; /* Вихід за межі U+10FFFF */
    } else {
        *p_src = s;
        return 0xFFFD; /* Невалідний лідируючий байт */
    }
    
    if ((size_t)(src_end - s) < needed) {
        *p_src = src_end;
        return 0xFFFD; /* Обрізаний потік байтів */
    }
    
    for (size_t i = 0; i < needed; ++i) {
        uint8_t bi = *s++;
        if ((bi & 0xC0) != 0x80) {
            *p_src = s;
            return 0xFFFD; /* Невірний байт продовження */
        }
        cp = (cp << 6) | (bi & 0x3F);
    }
    
    /* Перевірка на діапазон сурогатів UTF-16 та оверлонг для 3 байт */
    if ((cp >= 0xD800 && cp <= 0xDFFF) || (needed == 2 && cp < 0x0800) || (needed == 3 && cp < 0x10000)) {
        *p_src = s;
        return 0xFFFD;
    }
    
    *p_src = s;
    return cp;
}
