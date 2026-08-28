#include <stdint.h>

typedef int16_t q15_t;            // Q15: значення = x / 32768, діапазон [−1, +1)
#define Q              15
#define MU_SHIFT       9          // крок μ = 2⁻⁹ ≈ 0.002 (degree of learning)

static q15_t  wq[N]  = {0};       // коефіцієнти у Q15
static q15_t  xrq[N] = {0};       // кільце опорного, Q15
static q15_t  xsq[N] = {0};       // кільце filtered-x, Q15
static int    head_q = 0;

// насичувальне зведення 32-біт → Q15: за межами [−1,+1) тиснемо до краю,
// а НЕ обрізаємо біти (обрізання = перестрибування через діапазон, тріск)
static inline q15_t sat_q15(int32_t v)
{
    if (v >  32767) return  32767;
    if (v < -32768) return -32768;
    return (q15_t)v;
}

static q15_t fxlms_step_q15(q15_t ref, q15_t err)
{
    // 1) filtered-x: Ŝ ⊛ опорний, акумулятор 64-бітний
    int64_t accx = 0;
    for (int i = 0; i < M; ++i) {
        int idx = (head_q - 1 - i) & NMASK;
        accx += (int32_t)s_hat_q[i] * (int32_t)xrq[idx];   // Q15·Q15 = Q30
    }
    q15_t xprime = sat_q15((int32_t)(accx >> Q));          // Q30 → Q15

    // 2) кладемо нові відліки (O(1))
    xrq[head_q] = ref;
    xsq[head_q] = xprime;
    head_q = (head_q + 1) & NMASK;

    // 3) анти-шум: W ⊛ опорний
    int64_t accy = 0;
    for (int i = 0; i < N; ++i) {
        int idx = (head_q - 1 - i) & NMASK;
        accy += (int32_t)wq[i] * (int32_t)xrq[idx];        // Q30
    }
    q15_t y = sat_q15((int32_t)(accy >> Q));               // Q30 → Q15

    // 4) навчання у Q15 з leakage (про λ — нижче, у захисті):
    //    w ← w·(1 − leak)  +  μ · err · x′
    for (int i = 0; i < N; ++i) {
        int idx = (head_q - 1 - i) & NMASK;
        // крок: err·x′ це Q30; зводимо до Q15 (>>Q) і множимо на μ=2⁻ᵏ (>>MU_SHIFT)
        int32_t grad = ((int32_t)err * (int32_t)xsq[idx]) >> Q;   // Q15
        int32_t neww = (int32_t)wq[i] + (grad >> MU_SHIFT);       // + крок
        neww -= (neww >> LEAK_SHIFT);                             // − leakage (тяга до 0)
        wq[i] = sat_q15(neww);                                    // КЛАМП коефіцієнта
    }

    return y;
}
