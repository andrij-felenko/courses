#include <stdio.h>

#define N 2                 /* вузлів, окрім землі (вузол 0) */
static double G[N][N], rhs[N];

/* штамп резистора між вузлами a і b (0 = земля, його рядок не пишемо) */
static void stamp_R(int a, int b, double r) {
    double g = 1.0 / r;
    if (a) G[a-1][a-1] += g;
    if (b) G[b-1][b-1] += g;
    if (a && b) { G[a-1][b-1] -= g;  G[b-1][a-1] -= g; }
}
/* штамп джерела струму: тече з a в b (у правій частині) */
static void stamp_I(int a, int b, double i) {
    if (a) rhs[a-1] -= i;
    if (b) rhs[b-1] += i;
}
/* розв'язок G·x = rhs на місці, метод Гаусса з вибором головного елемента */
static void gauss(int n, double A[N][N], double b[N], double x[N]) {
    for (int c = 0; c < n; c++) {
        int piv = c;
        for (int r = c+1; r < n; r++)
            if (A[r][c]*A[r][c] > A[piv][c]*A[piv][c]) piv = r;
        for (int j = 0; j < n; j++) { double t=A[c][j]; A[c][j]=A[piv][j]; A[piv][j]=t; }
        double t=b[c]; b[c]=b[piv]; b[piv]=t;
        for (int r = 0; r < n; r++) if (r != c) {
            double f = A[r][c] / A[c][c];
            for (int j = c; j < n; j++) A[r][j] -= f * A[c][j];
            b[r] -= f * b[c];
        }
    }
    for (int i = 0; i < n; i++) x[i] = b[i] / A[i][i];
}

int main(void) {
    stamp_I(0, 1, 0.12);     /* 0.12 А у вузол 1            */
    stamp_R(1, 2, 100.0);    /* R1 між 1 і 2               */
    stamp_R(2, 0, 200.0);    /* R2 від 2 на землю          */
    double x[N];
    gauss(N, G, rhs, x);
    printf("V(1) = %.2f В\n", x[0]);   /* 36.00 В */
    printf("V(2) = %.2f В\n", x[1]);   /* 24.00 В */
    return 0;
}
