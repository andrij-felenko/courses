#include <math.h>
#include <stdint.h>

static int   sgn(float x)            { return x >= 0 ? 1 : -1; }
static float f_node(float a, float b) {                 // обережно: min-sum boxplus
    float m = fabsf(a) < fabsf(b) ? fabsf(a) : fabsf(b);
    return (float)(sgn(a) * sgn(b)) * m;
}
static float g_node(float a, float b, int u) {          // u — уже вирішений верхній біт
    return b + (float)(1 - 2 * u) * a;
}

/* llr[0..N) — довіри на виходах вузла; frozen[0..N) — маска (1 = заморожено).
   Пише вирішені біти в u[0..N), а кодове слово (частинкові суми) — у x[0..N). */
void sc_decode(const float *llr, const uint8_t *frozen,
               int N, uint8_t *u, uint8_t *x) {
    if (N == 1) {
        u[0] = frozen[0] ? 0 : (llr[0] >= 0 ? 0 : 1);
        x[0] = u[0];
        return;
    }
    int h = N / 2;
    float La[h], Lb[h];                 // для наочності — VLA; у продакшні статичні буфери
    uint8_t xa[h], xb[h];
    for (int i = 0; i < h; i++) La[i] = f_node(llr[i], llr[i + h]);   // f-прохід
    sc_decode(La, frozen, h, u, xa);                                 // верхня половина
    for (int i = 0; i < h; i++) Lb[i] = g_node(llr[i], llr[i + h], xa[i]); // g-прохід
    sc_decode(Lb, frozen + h, h, u + h, xb);                         // нижня половина
    for (int i = 0; i < h; i++) x[i]     = xa[i] ^ xb[i];            // зшити половини
    for (int i = 0; i < h; i++) x[i + h] = xb[i];
}
