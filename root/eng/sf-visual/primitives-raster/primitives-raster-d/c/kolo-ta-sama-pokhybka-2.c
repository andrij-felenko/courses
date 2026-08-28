static inline void plot8(uint16_t *fb, int W, int H,
                         int cx, int cy, int x, int y, uint16_t color)
{
    set_clip(fb, W, H, cx + x, cy + y, color);   // кожна точка ще й
    set_clip(fb, W, H, cx - x, cy + y, color);   // відсікається до екрана
    set_clip(fb, W, H, cx + x, cy - y, color);
    set_clip(fb, W, H, cx - x, cy - y, color);
    set_clip(fb, W, H, cx + y, cy + x, color);
    set_clip(fb, W, H, cx - y, cy + x, color);
    set_clip(fb, W, H, cx + y, cy - x, color);
    set_clip(fb, W, H, cx - y, cy - x, color);
}
