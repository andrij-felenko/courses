#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define N  8            /* розмір входу й виходу       */
#define H  3            /* розмір коду — вузьке горло  */
#define EPOCHS 6000
#define LR   1.0        /* темп навчання               */

static double W1[H][N], b1[H];   /* кодувальник:   x[8] -> z[3] */
static double W2[N][H], b2[N];   /* декодувальник: z[3] -> x̂[8] */

static double sigmoid(double t) { return 1.0 / (1.0 + exp(-t)); }

/* рівномірний шум у [-0.5, 0.5) — дрібна випадкова ініціалізація */
static double frand(void) { return (double)rand() / RAND_MAX - 0.5; }

static void init_weights(void)
{
    for (int j = 0; j < H; j++) {
        for (int k = 0; k < N; k++) W1[j][k] = 0.6 * frand();
        b1[j] = 0.0;
    }
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < H; j++) W2[i][j] = 0.6 * frand();
        b2[i] = 0.0;
    }
}
