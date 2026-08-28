#define WIN   15
#define RAD   (WIN / 2)        // = 7
#define CCONST 5               // запас C: піксель мусить бути помітно яскравішим за окіл

// Сума прямокутника [x1..x2]×[y1..y2] за чотири звернення до інтегралу.
static uint32_t rect_sum(int x1, int y1, int x2, int y2) {
    uint32_t a = I[y2][x2];
    uint32_t b = (x1 > 0)            ? I[y2][x1-1]   : 0;
    uint32_t c = (y1 > 0)            ? I[y1-1][x2]   : 0;
    uint32_t d = (x1 > 0 && y1 > 0)  ? I[y1-1][x1-1] : 0;
    return a - b - c + d;
}

void adaptive_threshold(const uint8_t gray[H][W], uint8_t mask[H][W]) {
    for (int y = 0; y < H; y++) {
        for (int x = 0; x < W; x++) {
            int x1 = x - RAD, y1 = y - RAD;
            int x2 = x + RAD, y2 = y + RAD;
            if (x1 < 0) x1 = 0;                 // обрізаємо вікно краєм кадру
            if (y1 < 0) y1 = 0;
            if (x2 >= W) x2 = W - 1;
            if (y2 >= H) y2 = H - 1;

            uint32_t area = (uint32_t)(x2 - x1 + 1) * (y2 - y1 + 1);
            uint32_t sum  = rect_sum(x1, y1, x2, y2);
            int      mean = (int)(sum / area);  // середня яскравість фактичного вікна
            int      thr  = mean - CCONST;      // локальний поріг T(x,y)

            mask[y][x] = (gray[y][x] > thr) ? 255 : 0;
        }
    }
}
