#define GRID 6                          // мітка 6×6 (рамка + 4×4 даних)
#define CANON 48                        // S: 8 пікселів на клітинку (GRID*8) — з запасом
#define IGN   0.13                      // відступ від краю клітинки (як у OpenCV)

// Прочитати сітку GRID×GRID: у cells[gy][gx] — середня яскравість серединки клітинки.
static void read_grid(const uint8_t *img, int W, int Himg,
                      const double Hi[9], int cells[GRID][GRID]) {
    const double cell = (double)CANON / GRID;
    const double m = cell * IGN;                    // поле, яке ігноруємо
    for (int gy = 0; gy < GRID; gy++)
        for (int gx = 0; gx < GRID; gx++) {
            double x0 = gx*cell + m, x1 = (gx+1)*cell - m;
            double y0 = gy*cell + m, y1 = (gy+1)*cell - m;
            long sum = 0; int cnt = 0;
            for (double Yc = y0 + 0.5; Yc < y1; Yc += 1.0)
                for (double Xc = x0 + 0.5; Xc < x1; Xc += 1.0) {
                    int v = sample_canonical(img, W, Himg, Hi, Xc, Yc);
                    if (v >= 0) { sum += v; cnt++; }
                }
            cells[gy][gx] = cnt ? (int)(sum / cnt) : 0;
        }
}

// Перетворити яскравості клітинок на біти bit[gy][gx] (1 = біле) спільним порогом.
// Поріг — середина між найтемнішою й найсвітлішою клітинками (стійко до світла).
static void cells_to_bits(const int cells[GRID][GRID], uint8_t bit[GRID][GRID]) {
    int lo = 255, hi = 0;
    for (int gy = 0; gy < GRID; gy++)
        for (int gx = 0; gx < GRID; gx++) {
            if (cells[gy][gx] < lo) lo = cells[gy][gx];
            if (cells[gy][gx] > hi) hi = cells[gy][gx];
        }
    int thr = (lo + hi) / 2;
    for (int gy = 0; gy < GRID; gy++)
        for (int gx = 0; gx < GRID; gx++)
            bit[gy][gx] = cells[gy][gx] > thr ? 1 : 0;   // світліше за поріг → біле
}
