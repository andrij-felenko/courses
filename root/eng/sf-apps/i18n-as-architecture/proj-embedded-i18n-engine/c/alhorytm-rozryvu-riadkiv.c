/* Знаходження точок розриву рядка для вміщення у задану ширину на C99 */
size_t emb_text_wrap(const embedded_font_t *font, const char *text, uint16_t max_width, 
                     uint16_t *line_offsets, size_t max_lines) {
    if (!font || !text || !line_offsets || max_lines == 0) return 0;
    
    size_t line_count = 0;
    line_offsets[line_count++] = 0;
    
    const uint8_t *src = (const uint8_t *)text;
    const uint8_t *end = src + strlen(text);
    const uint8_t *line_start = src;
    const uint8_t *last_space = NULL;
    
    uint16_t current_line_width = 0;
    uint16_t width_at_last_space = 0;
    
    while (src < end) {
        const uint8_t *char_start = src;
        uint32_t cp = utf8_decode_next(&src, end);
        if (cp == 0xFFFD) continue;
        
        if (cp == ' ') {
            last_space = char_start;
            width_at_last_space = current_line_width;
        }
        
        const font_glyph_desc_t *glyph = font_find_glyph(font, cp);
        uint8_t adv = glyph ? glyph->adv_w : 0;
        
        if (current_line_width + adv > max_width) {
            if (line_count >= max_lines) break;
            
            if (last_space && last_space > line_start) {
                /* Розриваємо рядок на останньому знайденому пробілі */
                line_offsets[line_count++] = (uint16_t)(last_space + 1 - (const uint8_t *)text);
                src = last_space + 1;
                line_start = src;
                last_space = NULL;
                current_line_width = 0;
            } else {
                /* Якщо слово довше за ширину екрана, розриваємо прямо по символу */
                line_offsets[line_count++] = (uint16_t)(char_start - (const uint8_t *)text);
                line_start = char_start;
                current_line_width = adv;
            }
        } else {
            current_line_width += adv;
        }
    }
    return line_count;
}
