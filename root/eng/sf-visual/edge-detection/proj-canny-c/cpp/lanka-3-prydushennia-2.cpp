// Білінійна сила в (точно дробовій) точці (fx, fy) — змішування 4 сусідів.
static double bilerp(int H, int W, const int *mag, double fy, double fx) {
    int x0 = (int)floor(fx), y0 = (int)floor(fy);
    if (x0 < 0 || y0 < 0 || x0 + 1 >= W || y0 + 1 >= H) return 0.0;
    double tx = fx - x0, ty = fy - y0;
    double top = mag[IDX(y0,   x0)] * (1 - tx) + mag[IDX(y0,   x0+1)] * tx;
    double bot = mag[IDX(y0+1, x0)] * (1 - tx) + mag[IDX(y0+1, x0+1)] * tx;
    return top * (1 - ty) + bot * ty;
}

// NMS із білінійною інтерполяцією двох сусідів уздовж напряму градієнта.
static void nms_interp(int H, int W, const int *mag,
                       const double *gx, const double *gy, int *out) {
    for (int i = 0; i < H * W; i++) out[i] = 0;
    for (int y = 1; y < H - 1; y++) {
        for (int x = 1; x < W - 1; x++) {
            int m = mag[IDX(y, x)];
            if (m == 0) continue;
            double n = sqrt(gx[IDX(y,x)] * gx[IDX(y,x)] + gy[IDX(y,x)] * gy[IDX(y,x)]);
            if (n < 1e-9) continue;
            double ux = gx[IDX(y, x)] / n, uy = gy[IDX(y, x)] / n;  // одиничний градієнт
            double f1 = bilerp(H, W, mag, y + uy, x + ux);          // вперед
            double f2 = bilerp(H, W, mag, y - uy, x - ux);          // назад
            if (m >= f1 && m >= f2) out[IDX(y, x)] = m;
        }
    }
}
