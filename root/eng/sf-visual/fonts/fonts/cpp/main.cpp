// Кадровий буфер RGB565: WIDTH×HEIGHT, рядок за рядком
uint16_t fb[WIDTH * HEIGHT];

// Один гліф 8×8: 8 байтів, старший біт — лівий піксель рядка
void blit_glyph(int x, int y, const uint8_t glyph[8], uint16_t color) {
    for (int row = 0; row < 8; row++) {
        uint8_t bits = glyph[row];          // рядок гліфа
        for (int col = 0; col < 8; col++) {
            if (bits & (0x80 >> col))       // біт виставлено → піксель чорний
                fb[(y + row) * WIDTH + (x + col)] = color;
        }
    }
}

// Рядок тексту: блітнути гліф і зсунути курсор на крок (тут моноширинний — 8)
void draw_text(int x, int y, const char *s, uint16_t color) {
    int cursor = x;
    for (; *s; s++) {
        const uint8_t *g = font8x8[(uint8_t)*s];  // код символу → 8 байтів гліфа
        blit_glyph(cursor, y, g, color);
        cursor += 8;                              // advance: наступна літера праворуч
    }
}
