// Адаптивний поріг ADAPTIVE_THRESH_MEAN_C через інтегральне зображення.
// out[i] = 1, якщо піксель ТЕМНІШИЙ за (локальне середнє − C): це «чорнило» мітки.
// win — сторона вікна (непарна), у OpenCV-aruco її беруть у діапазоні 3..23.
// integ — буфер (W+1)*(H+1) на 32-бітних сумах; викликач виділяє його раз.
static void adaptive_threshold(const uint8_t *img, int W, int H,
                               int win, int C, uint8_t *out, uint32_t *integ) {
    const int IW = W + 1;
    // 1) Інтегральне зображення: integ[y+1][x+1] = сума всіх пікселів лівіше-вище.
    for (int x = 0; x <= W; x++) integ[x] = 0;          // нульовий рядок
    for (int y = 0; y < H; y++) {
        uint32_t row = 0;
        integ[(y + 1) * IW] = 0;                        // нульовий стовпець
        for (int x = 0; x < W; x++) {
            row += img[y * W + x];
            integ[(y + 1) * IW + (x + 1)] = integ[y * IW + (x + 1)] + row;
        }
    }
    // 2) Для кожного пікселя — середнє по вікну навколо, порівняння з C.
    const int r = win / 2;
    for (int y = 0; y < H; y++) {
        for (int x = 0; x < W; x++) {
            int x0 = x - r < 0 ? 0 : x - r,  y0 = y - r < 0 ? 0 : y - r;
            int x1 = x + r >= W ? W - 1 : x + r,  y1 = y + r >= H ? H - 1 : y + r;
            int area = (x1 - x0 + 1) * (y1 - y0 + 1);
            // сума по прямокутнику [x0..x1]×[y0..y1] — чотири кути таблиці:
            uint32_t s = integ[(y1 + 1) * IW + (x1 + 1)]
                       - integ[(y0    ) * IW + (x1 + 1)]
                       - integ[(y1 + 1) * IW + (x0    )]
                       + integ[(y0    ) * IW + (x0    )];
            int mean = (int)(s / (uint32_t)area);
            out[y * W + x] = (img[y * W + x] < mean - C) ? 1 : 0;   // темніше → «чорнило»
        }
    }
}
