#include <math.h>
#include <stdio.h>

// Структура параметрів активного ФНЧ 2-го порядку Саллена-Кея
typedef struct {
    double cutoff_freq_hz; // Частота зрізу f0 (Гц)
    double r1_ohms;        // Резистор R1 (Ом)
    double r2_ohms;        // Резистор R2 (Ом)
    double c1_farads;      // Конденсатор C1 (Ф)
    double c2_farads;      // Конденсатор C2 (Ф)
    double damping_Q;      // Добротність Q (0.707 для Баттерворта)
} sallen_key_filter_t;

// Розрахунок номіналів для фільтра Баттерворта (R1 = R2 = R, C1 = 2*C2)
void calculate_sallen_key_butterworth(double target_f0, double c2_val, sallen_key_filter_t *filt) {
    filt->cutoff_freq_hz = target_f0;
    filt->c2_farads = c2_val;
    filt->c1_farads = 2.0 * c2_val; // Для Q = 0.707 при однаковому R
    filt->r1_ohms = 1.0 / (2.0 * M_PI * target_f0 * c2_val * sqrt(2.0));
    filt->r2_ohms = filt->r1_ohms;
    filt->damping_Q = 1.0 / sqrt(2.0); // Q = 0.7071
}
