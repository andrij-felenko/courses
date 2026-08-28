#include <stdint.h>

// RGB888 -> HSV, кожен канал 0..255. Тон закодовано як 0..255 (увесь круг у байт).
// Без float. Усі проміжні int32_t — проти переповнення масштабування.
void rgb_to_hsv_u8(uint8_t r, uint8_t g, uint8_t b,
                   uint8_t *h, uint8_t *s, uint8_t *v) {
    int32_t cmax = r > g ? (r > b ? r : b) : (g > b ? g : b);
    int32_t cmin = r < g ? (r < b ? r : b) : (g < b ? g : b);
    int32_t delta = cmax - cmin;

    *v = (uint8_t)cmax;                       // V = Cmax

    if (cmax == 0) { *s = 0; *h = 0; return; } // чорне: S,H не визначені
    *s = (uint8_t)((delta * 255) / cmax);      // S = Δ/Cmax, масштаб ×255

    if (delta == 0) { *h = 0; return; }        // сіре: тон не визначений

    // тон рахуємо у проміжній шкалі 0..1530 (6 секторів по 255), тоді /6 у 0..255
    int32_t hue;
    if (cmax == r)      hue = 0    + (255 * (g - b)) / delta;  // червоний сектор
    else if (cmax == g) hue = 510  + (255 * (b - r)) / delta;  // зелений  (+2·255)
    else                hue = 1020 + (255 * (r - g)) / delta;  // синій    (+4·255)

    if (hue < 0) hue += 1530;                  // загорнути від'ємний бік (≡ mod 6)
    *h = (uint8_t)(hue / 6);                   // 1530 → 255
}
