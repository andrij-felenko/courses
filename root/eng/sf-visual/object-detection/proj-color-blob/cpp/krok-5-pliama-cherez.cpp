struct Blob { bool found; int cx, cy, area; int x0, y0, x1, y1; };

static Blob find_blob(const uint8_t *m, int min_area) {
    long M00 = 0, M10 = 0, M01 = 0;                      // широкий тип: суми не переповнюються
    int x0 = W, y0 = H, x1 = 0, y1 = 0;
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++)
            if (m[y*W + x]) {
                M00 += 1;  M10 += x;  M01 += y;          // моменти
                if (x < x0) x0 = x;   if (x > x1) x1 = x; // габарити
                if (y < y0) y0 = y;   if (y > y1) y1 = y;
            }
    Blob b = {};
    if (M00 < min_area) return b;        // замало пікселів — це шум, не ціль
    b.found = true;
    b.area  = static_cast<int>(M00);
    b.cx    = static_cast<int>(M10 / M00);  // центроїд
    b.cy    = static_cast<int>(M01 / M00);
    b.x0 = x0; b.y0 = y0; b.x1 = x1; b.y1 = y1;
    return b;
}
