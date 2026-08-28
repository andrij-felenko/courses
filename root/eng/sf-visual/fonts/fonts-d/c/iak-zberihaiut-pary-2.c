int draw_text_kerned(uint16_t *fb, int penX, int penY,
                     const Font *font, const KernPair *kt, int kn,
                     const char *s, uint16_t color) {
    for (int i = 0; s[i]; i++) {
        penX = draw_glyph(fb, penX, penY, font, s[i], color);
        if (s[i + 1])                            // є наступна літера?
            penX += kern(kt, kn, s[i], s[i + 1]); // підсунути за таблицею пар
    }
    return penX;
}
