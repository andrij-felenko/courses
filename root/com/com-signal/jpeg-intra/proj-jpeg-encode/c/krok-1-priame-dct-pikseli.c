static double A[8][8];              /* косинусна матриця; будуємо раз */

static void build_dct_matrix(void) {
    for (int k = 0; k < 8; k++) {
        double a = (k == 0) ? sqrt(1.0 / 8.0) : sqrt(2.0 / 8.0);
        for (int n = 0; n < 8; n++)
            A[k][n] = a * cos((2 * n + 1) * k * M_PI / 16.0);
    }
}

/* F = A · f · Aᵀ : спершу стовпці (t = A·f), тоді рядки (F = t·Aᵀ) */
static void fdct(const double f[8][8], double F[8][8]) {
    double t[8][8];
    for (int u = 0; u < 8; u++)
        for (int y = 0; y < 8; y++) {
            double s = 0.0;
            for (int x = 0; x < 8; x++) s += A[u][x] * f[x][y];
            t[u][y] = s;
        }
    for (int u = 0; u < 8; u++)
        for (int v = 0; v < 8; v++) {
            double s = 0.0;
            for (int y = 0; y < 8; y++) s += t[u][y] * A[v][y];
            F[u][v] = s;
        }
}
