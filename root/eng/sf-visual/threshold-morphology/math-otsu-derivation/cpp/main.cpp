#include <stdint.h>

// hist[L] — гістограма (лічба пікселів), N — усього пікселів.
// Повертає поріг t: пікселі з яскравістю > t — об'єкт.
int otsu_threshold(const uint32_t hist[], int L, uint32_t N) {
    uint64_t sum_total = 0;                 // Σ i·n_i по всій гістограмі
    for (int i = 0; i < L; i++) sum_total += (uint64_t)i * hist[i];

    uint64_t sum_bg = 0;                    // накопичений момент S(t)·N
    uint32_t w_bg   = 0;                    // накопичена вага w₀·N
    double   best_var = -1.0;
    int      best_t   = 0;

    for (int t = 0; t < L; t++) {
        w_bg   += hist[t];                  // w₀·N наростанням
        if (w_bg == 0) continue;            // клас тла ще порожній
        uint32_t w_fg = N - w_bg;           // w₁·N
        if (w_fg == 0) break;               // клас об'єкта спорожнів — далі нема сенсу

        sum_bg += (uint64_t)t * hist[t];    // S(t)·N наростанням
        double mu_bg = (double)sum_bg / w_bg;
        double mu_fg = (double)(sum_total - sum_bg) / w_fg;

        // σ²_b ∝ w₀·w₁·(μ₀−μ₁)²  (спільний дільник N² відкинуто)
        double diff = mu_bg - mu_fg;
        double var_between = (double)w_bg * w_fg * diff * diff;

        if (var_between > best_var) {        // запам'ятати вершину горба
            best_var = var_between;
            best_t   = t;
        }
    }
    return best_t;
}
