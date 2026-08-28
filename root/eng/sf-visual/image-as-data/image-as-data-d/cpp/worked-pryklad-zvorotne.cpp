// YCbCr (BT.601, limited range) -> RGB888, цілочисельно (масштаб 256)
// Коефіцієнти домножені на 256: 1.164→298, 1.596→409, 0.392→100, 0.813→208, 2.017→516
static inline uint8_t clamp_u8(int32_t v) {
    return v < 0 ? 0 : (v > 255 ? 255 : (uint8_t)v);
}

static void ycbcr_to_rgb(int Y, int Cb, int Cr,
                         uint8_t *r, uint8_t *g, uint8_t *b) {
    int32_t c = 298 * (Y  - 16);     // спільний доданок яскравості
    int32_t d = Cb - 128;            // колірність, центрована на 0
    int32_t e = Cr - 128;
    *r = clamp_u8((c + 409 * e            + 128) >> 8);
    *g = clamp_u8((c - 100 * d - 208 * e  + 128) >> 8);
    *b = clamp_u8((c + 516 * d            + 128) >> 8);
}
