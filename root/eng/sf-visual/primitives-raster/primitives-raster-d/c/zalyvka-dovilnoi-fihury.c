// Заливка многокутника по рядках. poly[] — N вершин (x,y) за обходом.
void fill_polygon(uint16_t *fb, int W, int H,
                  const Point *poly, int N, uint16_t color)
{
    // межі по Y — лише рядки, які фігура справді накриває
    int ymin = INT_MAX, ymax = INT_MIN;
    for (int i = 0; i < N; i++) {
        if (poly[i].y < ymin) ymin = poly[i].y;
        if (poly[i].y > ymax) ymax = poly[i].y;
    }
    if (ymin < 0) ymin = 0;
    if (ymax > H - 1) ymax = H - 1;

    int xs[MAX_X];                         // перетини поточного рядка
    for (int y = ymin; y <= ymax; y++) {
        int n = 0;
        // зібрати x-перетини ребер із серединою рядка (y + 0.5)
        for (int i = 0, j = N - 1; i < N; j = i++) {
            int yi = poly[i].y, yj = poly[j].y;
            // ребро перетинає рядок, якщо y між його кінцями (півінтервал!)
            if ((yi <= y && yj > y) || (yj <= y && yi > y)) {
                // лінійна інтерполяція x у точці перетину
                int xi = poly[i].x + (long)(y - yi) * (poly[j].x - poly[i].x)
                                     / (yj - yi);
                xs[n++] = xi;
            }
        }
        // посортувати перетини зліва направо (n мале — досить вставками)
        for (int a = 1; a < n; a++) {
            int v = xs[a], b = a - 1;
            while (b >= 0 && xs[b] > v) { xs[b + 1] = xs[b]; b--; }
            xs[b + 1] = v;
        }
        // залити спани між парами 0-1, 2-3, ...
        for (int a = 0; a + 1 < n; a += 2)
            hspan(fb, W, H, xs[a], xs[a + 1], y, color);
    }
}
