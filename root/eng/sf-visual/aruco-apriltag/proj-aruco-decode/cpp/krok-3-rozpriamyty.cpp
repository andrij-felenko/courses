// Розв'язати A·x = b, A — n×n (рядки поспіль), методом Гаусса з вибором ведучого.
// Повертає 0, якщо матриця вироджена (кандидат геть плаский — не мітка).
static int solve_linear(double *A, double *b, double *x, int n) {
    for (int col = 0; col < n; col++) {
        // вибір ведучого рядка (найбільший за модулем елемент у стовпці) — стійкість
        int piv = col; double mx = fabs(A[col * n + col]);
        for (int r = col + 1; r < n; r++) {
            double v = fabs(A[r * n + col]);
            if (v > mx) { mx = v; piv = r; }
        }
        if (mx < 1e-9) return 0;                 // вироджена → відкинути кандидата
        if (piv != col) {                        // переставити рядки piv ↔ col
            for (int k = 0; k < n; k++) { double t = A[col*n+k]; A[col*n+k] = A[piv*n+k]; A[piv*n+k] = t; }
            double t = b[col]; b[col] = b[piv]; b[piv] = t;
        }
        double d = A[col * n + col];
        for (int r = 0; r < n; r++) {            // виключити стовпець з решти рядків
            if (r == col) continue;
            double f = A[r * n + col] / d;
            for (int k = col; k < n; k++) A[r*n+k] -= f * A[col*n+k];
            b[r] -= f * b[col];
        }
    }
    for (int i = 0; i < n; i++) x[i] = b[i] / A[i * n + i];   // діагональ → розв'язок
    return 1;
}

// Гомографія, що переводить 4 кути мітки src[4] у квадрат [0..S]×[0..S].
// H (9 елементів, h8=1) записуємо в out. S — сторона канонічного квадрата в пікселях.
static int homography_to_square(const Pt src[4], int S, double H[9]) {
    const double dst[4][2] = { {0,0}, {(double)S,0}, {(double)S,(double)S}, {0,(double)S} };
    double A[64], b[8];
    for (int i = 0; i < 4; i++) {
        double xs = src[i].x, ys = src[i].y, X = dst[i][0], Y = dst[i][1];
        double *r0 = &A[(2*i)   * 8], *r1 = &A[(2*i+1) * 8];
        r0[0]=xs; r0[1]=ys; r0[2]=1; r0[3]=0;  r0[4]=0;  r0[5]=0; r0[6]=-X*xs; r0[7]=-X*ys; b[2*i]  =X;
        r1[0]=0;  r1[1]=0;  r1[2]=0; r1[3]=xs; r1[4]=ys; r1[5]=1; r1[6]=-Y*xs; r1[7]=-Y*ys; b[2*i+1]=Y;
    }
    double h[8];
    if (!solve_linear(A, b, h, 8)) return 0;
    for (int i = 0; i < 8; i++) H[i] = h[i];
    H[8] = 1.0;
    return 1;
}
