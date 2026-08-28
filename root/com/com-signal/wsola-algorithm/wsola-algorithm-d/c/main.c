#include <stdint.h>

/* Пошук оптимального зміщення δ за критерієм максимуму кореляції.
   ref_buf  — вказівник на початок еталонного шаблону x[τ_{k-1} + Hs]
   cand_buf — вказівник на початок області пошуку x[k*Ha - seek_range]
   L        — довжина шаблону (template_size)
   seek     — радіус пошуку Δ (seek_range)
*/
int wsola_find_best_shift_c(const float *ref_buf, const float *cand_buf, int L, int seek) {
    float max_corr = -1e30f;
    int best_delta = 0;

    for (int d = -seek; d <= seek; ++d) {
        const float *cand = cand_buf + (d + seek);
        float corr = 0.0f;

        /* Внутрішній цикл: обчислення скалярного добутку векторів */
        for (int m = 0; m < L; ++m) {
            corr += ref_buf[m] * cand[m];
        }

        if (corr > max_corr) {
            max_corr = corr;
            best_delta = d;
        }
    }

    return best_delta;
}
