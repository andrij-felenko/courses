// Прочитати один UTF-8 символ з рядка; *i просунути на спожиті байти.
// Повертає код символу (codepoint).
uint32_t utf8_next(const char *s, int *i) {
    uint8_t b0 = s[*i];
    if (b0 < 0x80) { (*i)++; return b0; }                    // 1 байт — латиниця
    if ((b0 & 0xE0) == 0xC0) {                               // 2 байти — кирилиця тощо
        uint32_t cp = ((b0 & 0x1F) << 6) | (s[*i + 1] & 0x3F);
        *i += 2; return cp;
    }
    if ((b0 & 0xF0) == 0xE0) {                               // 3 байти
        uint32_t cp = ((b0 & 0x0F) << 12) | ((s[*i + 1] & 0x3F) << 6)
                                          |  (s[*i + 2] & 0x3F);
        *i += 3; return cp;
    }
    uint32_t cp = ((b0 & 0x07) << 18) | ((s[*i + 1] & 0x3F) << 12)   // 4 байти
                | ((s[*i + 2] & 0x3F) << 6) | (s[*i + 3] & 0x3F);
    *i += 4; return cp;
}
