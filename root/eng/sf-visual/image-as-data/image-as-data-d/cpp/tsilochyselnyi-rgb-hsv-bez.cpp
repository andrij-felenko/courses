#include <stdint.h>

// RGB888 -> HSV, усе в 0..255. H закодовано як 0..255 (а не 0..360°).
static void rgb_to_hsv_u8(uint8_t r, uint8_t g, uint8_t b,
                          uint8_t *h, uint8_t *s, uint8_t *v) {
    int32_t cmax = r > g ? (r > b ? r : b) : (g > b ? g : b);   // max каналу
    int32_t cmin = r < g ? (r < b ? r : b) : (g < b ? g : b);   // min каналу
    int32_t delta = cmax - cmin;

    *v = (uint8_t)cmax;                          // V = Cmax

    if (cmax == 0) { *s = 0; *h = 0; return; }   // чорне: S,H не визначені → 0
    *s = (uint8_t)((delta * 255) / cmax);        // S = Δ/Cmax, масштаб ×255

    if (delta == 0) { *h = 0; return; }          // сіре: тон не визначений → 0

    int32_t hue;   // рахуємо тон у 0..1530 (6 секторів по 255), тоді стиснемо до 0..255
    if (cmax == r)      hue = 0    + (255 * (g - b)) / delta;   // червоний сектор
    else if (cmax == g) hue = 510  + (255 * (b - r)) / delta;   // зелений  (+2·255)
    else                hue = 1020 + (255 * (r - g)) / delta;   // синій    (+4·255)

    if (hue < 0) hue += 1530;                    // загорнути від'ємний бік (як mod 6)
    *h = (uint8_t)(hue / 6);                     // 0..1530 → 0..255
}
