typedef enum {
    FMT_RGB332 = 8,    /* 8 біт  → 1 байт/піксель  */
    FMT_RGB565 = 16,   /* 16 біт → 2 байти/піксель ← стандарт вбудованих */
    FMT_RGB888 = 24,   /* 24 біти → 3 байти/піксель */
} ColorFormat;

/* глибина в бітах → байтів на піксель (округлення вгору) */
static uint32_t bytes_per_pixel(ColorFormat bpp)
{
    return ((uint32_t)bpp + 7u) / 8u;   /* (bpp+7)/8: 8→1, 16→2, 24→3 */
}
