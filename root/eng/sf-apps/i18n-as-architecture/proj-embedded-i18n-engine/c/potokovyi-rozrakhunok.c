/* Розрахунок геометричної ширини локалізованого рядка у пікселях на C99 */
uint16_t emb_font_get_string_width(const embedded_font_t *font, const char *utf8_str) {
    if (!font || !utf8_str) return 0;
    
    uint16_t total_width = 0;
    const uint8_t *src = (const uint8_t *)utf8_str;
    const uint8_t *end = src + strlen(utf8_str);
    
    while (src < end) {
        uint32_t cp = utf8_decode_next(&src, end);
        if (cp == 0xFFFD) continue;
        
        const font_glyph_desc_t *glyph = font_find_glyph(font, cp);
        if (glyph) {
            total_width += glyph->adv_w;
        }
    }
    return total_width;
}
