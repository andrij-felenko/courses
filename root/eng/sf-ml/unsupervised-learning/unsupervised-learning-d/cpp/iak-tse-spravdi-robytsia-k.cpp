// pts[N] — точки, cent[K] — центри, assign[N] — вихід
// повертає, скільки точок змінили групу (0 => можна спинятись)
int assign_step(const Pt *pts, int N, const Pt *cent, int K, int *assign) {
    int changed = 0;
    for (int i = 0; i < N; i++) {
        int    best  = 0;
        double bestd = 1e300;          // квадрат відстані до найближчого
        for (int c = 0; c < K; c++) {
            double dx = pts[i].x - cent[c].x;
            double dy = pts[i].y - cent[c].y;
            double d  = dx*dx + dy*dy;  // корінь брати не треба: порядок той самий
            if (d < bestd) { bestd = d; best = c; }
        }
        if (assign[i] != best) { assign[i] = best; changed++; }
    }
    return changed;
}
