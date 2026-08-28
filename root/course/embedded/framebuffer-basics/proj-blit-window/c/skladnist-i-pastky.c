#define SCR_W 240
#define SCR_H 320

/* Безпечна заливка: обрізає прямокутник до екрана, відкидає вироджений. */
static void fill_rect_safe(int x0, int y0, int x1, int y1, uint16_t color)
{
    if (x0 < 0) x0 = 0;   if (y0 < 0) y0 = 0;          // не лізти ліворуч/вгору
    if (x1 > SCR_W - 1) x1 = SCR_W - 1;                // не лізти за правий край
    if (y1 > SCR_H - 1) y1 = SCR_H - 1;               // не лізти за нижній край
    if (x0 > x1 || y0 > y1) return;                    // весь прямокутник за екраном
    fill_rect((uint16_t)x0, (uint16_t)y0,
              (uint16_t)x1, (uint16_t)y1, color);
}
