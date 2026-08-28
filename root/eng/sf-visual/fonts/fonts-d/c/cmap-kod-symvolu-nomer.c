int draw_utf8_line(uint16_t *fb, int penX, int penY,
                   const Font *font, const CmapRange *cmap, int cn,
                   const char *s, uint16_t color) {
    int i = 0;
    while (s[i]) {
        uint32_t cp = utf8_next(s, &i);            // байти → код символу
        int gi = cmap_lookup(cmap, cn, cp);        // код → номер гліфа
        if (gi < 0) gi = cmap_lookup(cmap, cn, '?'); // нема — запасний
        penX = draw_glyph_by_index(fb, penX, penY, font, gi, color);
        // (кернінг за бажанням: + kern(...) для пари номерів гліфів)
    }
    return penX;
}
