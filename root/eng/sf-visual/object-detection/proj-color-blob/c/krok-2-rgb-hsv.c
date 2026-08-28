typedef struct { uint8_t h2, s, v; } Hsv;  // h2 = тон/2 (0..179), влазить у байт

static Hsv rgb_to_hsv(uint8_t r, uint8_t g, uint8_t b) {
    uint8_t mx = r > g ? (r > b ? r : b) : (g > b ? g : b);
    uint8_t mn = r < g ? (r < b ? r : b) : (g < b ? g : b);
    uint8_t d  = mx - mn;                 // хрома
    Hsv out;
    out.v = mx;                                          // яскравість = max
    out.s = mx ? (uint8_t)(255 * (int)d / mx) : 0;       // насиченість
    if (d == 0) { out.h2 = 0; return out; }              // сірий: тон не визначений

    int h;                                               // тон у градусах 0..359
    if (mx == r)      h = 60 * ((int)g - b) / d;         // сектор навколо червоного
    else if (mx == g) h = 120 + 60 * ((int)b - r) / d;   // навколо зеленого
    else              h = 240 + 60 * ((int)r - g) / d;   // навколо синього
    if (h < 0) h += 360;
    out.h2 = (uint8_t)(h / 2);                           // ділимо на 2, щоб влізло в 0..179
    return out;
}
