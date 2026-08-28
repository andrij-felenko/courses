// Накласти піксель тексту з покриттям cov (0..15) на фон у кадровому буфері.
// RGB565: 5 біт R, 6 біт G, 5 біт B. fg — колір тексту, bg — поточний піксель.
uint16_t blend565(uint16_t fg, uint16_t bg, uint8_t cov /*0..15*/) {
    uint16_t a = cov;                         // альфа 0..15
    uint16_t ia = 15 - a;                     // обернена
    uint16_t fr = (fg >> 11) & 0x1F, fgc = (fg >> 5) & 0x3F, fb = fg & 0x1F;
    uint16_t br = (bg >> 11) & 0x1F, bgc = (bg >> 5) & 0x3F, bb = bg & 0x1F;
    uint16_t r = (fr * a + br * ia) / 15;
    uint16_t gg = (fgc * a + bgc * ia) / 15;
    uint16_t b = (fb * a + bb * ia) / 15;
    return (r << 11) | (gg << 5) | b;
}
