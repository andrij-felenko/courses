// Безпечне читання маски: координати за межами затискаються до краю (clamp).
// Жодного звернення поза масивом — головне правило вбудованого коду.
static uint8_t at_clamp(const uint8_t m[H][W], int y, int x) {
    if (x < 0) x = 0; else if (x >= W) x = W - 1;
    if (y < 0) y = 0; else if (y >= H) y = H - 1;
    return m[y][x];
}

void erode3(const uint8_t src[H][W], uint8_t dst[H][W]) {
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            uint8_t mn = 255;                          // ерозія = мінімум по 3×3
            for (int dy = -1; dy <= 1; dy++)
                for (int dx = -1; dx <= 1; dx++) {
                    uint8_t v = at_clamp(src, y+dy, x+dx);
                    if (v < mn) mn = v;
                }
            dst[y][x] = mn;
        }
}

void dilate3(const uint8_t src[H][W], uint8_t dst[H][W]) {
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            uint8_t mx = 0;                             // дилатація = максимум по 3×3
            for (int dy = -1; dy <= 1; dy++)
                for (int dx = -1; dx <= 1; dx++) {
                    uint8_t v = at_clamp(src, y+dy, x+dx);
                    if (v > mx) mx = v;
                }
            dst[y][x] = mx;
        }
}
