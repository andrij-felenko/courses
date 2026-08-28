typedef struct {
    uint16_t bitmapOffset;   // зсув карти цього гліфа у спільному масиві бітів
    uint8_t  width, height;  // розміри карти, пікселів
    uint8_t  advance;        // крок курсора після гліфа
    int8_t   xOffset, yOffset; // зсув карти відносно курсора (зі знаком!)
} GlyphInfo;

typedef struct {
    const uint8_t   *bitmap;   // спільний масив бітів усіх гліфів
    const GlyphInfo *glyphs;   // таблиця метрик, паралельна діапазону символів
    uint16_t first, last;      // діапазон кодів символів (напр. 0x20..0x7E)
    uint8_t  yAdvance;         // міжрядковий інтервал (висота рядка)
} Font;
