// Намалювати один гліф 1 біт/піксель з повними метриками.
// penX, penY — курсор на базовій лінії. Повертає новий penX.
int draw_glyph(uint16_t *fb, int penX, int penY,
               const Font *font, char ch, uint16_t color) {
    if ((uint8_t)ch < font->first || (uint8_t)ch > font->last)
        ch = '?';                                   // нема гліфа — підставити запасний
    const GlyphInfo *g = &font->glyphs[(uint8_t)ch - font->first];
    const uint8_t *bmp = &font->bitmap[g->bitmapOffset];

    int rowBytes = (g->width + 7) >> 3;             // ceil(width/8)
    int x0 = penX + g->xOffset;                     // лівий край карти
    int y0 = penY - g->yOffset;                     // верх карти (вгору від базової лінії)

    for (int row = 0; row < g->height; row++) {
        const uint8_t *rowData = &bmp[row * rowBytes];
        for (int col = 0; col < g->width; col++) {
            if (rowData[col >> 3] & (0x80 >> (col & 7)))   // біт виставлено?
                fb[(y0 + row) * FB_W + (x0 + col)] = color;
        }
    }
    return penX + g->advance;                        // курсор на наступну літеру
}
