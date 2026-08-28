#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t unicode_first;
    uint32_t unicode_last;
    uint32_t glyph_index_offset;
} font_unicode_range_t;

typedef struct {
    uint8_t  box_w;       /* Ширина растру в пікселях */
    uint8_t  box_h;       /* Висота растру в пікселях */
    int8_t   off_x;       /* Горизонтальний зсув від курсора (Bearing X) */
    int8_t   off_y;       /* Вертикальний зсув від базової лінії */
    uint8_t  adv_w;       /* Крок курсора (Advance Width) */
    uint8_t  reserved;
    uint32_t bitmap_offset; /* Зміщення бітів у загальному потоці Flash */
} font_glyph_desc_t;

typedef struct {
    uint32_t magic;           /* 0x464F4E54 ('FONT') */
    uint8_t  version;
    uint8_t  bpp;             /* 1, 2, 4 або 8 біт на піксель */
    int8_t   ascent;          /* Висота над базовою лінією */
    int8_t   descent;         /* Глибина під базовою лінією */
    uint16_t range_count;
    uint32_t glyph_count;
    const font_unicode_range_t *ranges;
    const font_glyph_desc_t    *glyphs;
    const uint8_t              *bitmap_data;
} embedded_font_t;

const font_glyph_desc_t *font_find_glyph(const embedded_font_t *font, uint32_t codepoint) {
    if (!font || !font->ranges || !font->glyphs) return NULL;
    
    for (uint32_t r = 0; r < font->range_count; ++r) {
        if (codepoint >= font->ranges[r].unicode_first && 
            codepoint <= font->ranges[r].unicode_last) {
            uint32_t idx = font->ranges[r].glyph_index_offset + 
                           (codepoint - font->ranges[r].unicode_first);
            if (idx < font->glyph_count) {
                return &font->glyphs[idx];
            }
            break;
        }
    }
    return NULL; /* Символ відсутній у шрифті */
}
