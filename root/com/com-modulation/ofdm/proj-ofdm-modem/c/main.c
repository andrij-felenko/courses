#include <complex.h>
#include <math.h>
#define N  64                             /* піднесних = розмір FFT */

/* Ітеративне ШПФ Кулі–Тьюкі по місцю; inv != 0 — зворотне (з діленням на N). */
static void fft(double complex *x, int inv) {
    for (int i = 1, j = 0; i < N; i++) {          /* біт-реверсна перестановка */
        int bit = N >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j |= bit;
        if (i < j) { double complex t = x[i]; x[i] = x[j]; x[j] = t; }
    }
    for (int len = 2; len <= N; len <<= 1) {       /* стадії «метелика» */
        double ang = (inv ? 2.0 : -2.0) * M_PI / len;
        double complex wl = cos(ang) + I*sin(ang);
        for (int st = 0; st < N; st += len) {
            double complex w = 1.0;
            for (int k = 0; k < len/2; k++) {
                double complex u = x[st+k], v = x[st+k+len/2] * w;
                x[st+k] = u + v;  x[st+k+len/2] = u - v;  w *= wl;
            }
        }
    }
    if (inv) for (int i = 0; i < N; i++) x[i] /= N;
}

/* Передавач: 2N біт → блок із L-відліковим циклічним префіксом (L+N відліків). */
void tx(const int bits[2*N], int L, double complex block[]) {
    double complex S[N];
    for (int k = 0; k < N; k++)                            /* QPSK */
        S[k] = ((1 - 2*bits[2*k]) + I*(1 - 2*bits[2*k+1])) / sqrt(2.0);
    fft(S, 1);                                             /* IFFT… */
    for (int k = 0; k < N; k++) S[k] *= sqrt((double)N);   /* …·√N */
    for (int i = 0; i < L; i++) block[i]   = S[N-L+i];     /* хвіст → у префікс */
    for (int i = 0; i < N; i++) block[L+i] = S[i];
}

/* Приймач: блок → 2N біт; zero-forcing за відомим H[k] = FFT(h). */
void rx(const double complex block[], int L, const double complex H[N], int bits[2*N]) {
    double complex Y[N];
    for (int k = 0; k < N; k++) Y[k] = block[L+k];         /* зняти префікс */
    fft(Y, 0);                                             /* FFT… */
    for (int k = 0; k < N; k++) {
        double complex Sh = (Y[k] / sqrt((double)N)) / H[k];  /* …/√N, поділ на канал */
        bits[2*k]   = creal(Sh) < 0;                       /* зріз у біти */
        bits[2*k+1] = cimag(Sh) < 0;
    }
}
