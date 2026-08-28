#include <stdint.h>

// HSV (кожен 0..255, тон — увесь круг у байт) -> RGB888. Без float, без ділення в циклі.
void hsv_to_rgb_u8(uint8_t h, uint8_t s, uint8_t v,
                   uint8_t *r, uint8_t *g, uint8_t *b) {
    if (s == 0) { *r = *g = *b = v; return; }   // сіре: усі канали = V

    int32_t region = h / 43;            // 256/6 ≈ 43 → номер сектора 0..5
    int32_t rem    = (h - region * 43) * 6;     // залишок у 0..255 усередині сектора

    int32_t p = (v * (255 - s)) >> 8;                       // нижній рівень
    int32_t q = (v * (255 - ((s * rem) >> 8))) >> 8;        // спадна складова
    int32_t t = (v * (255 - ((s * (255 - rem)) >> 8))) >> 8; // висхідна складова

    switch (region) {
        case 0:  *r = v; *g = t; *b = p; break;
        case 1:  *r = q; *g = v; *b = p; break;
        case 2:  *r = p; *g = v; *b = t; break;
        case 3:  *r = p; *g = q; *b = v; break;
        case 4:  *r = t; *g = p; *b = v; break;
        default: *r = v; *g = p; *b = q; break;   // case 5
    }
}
