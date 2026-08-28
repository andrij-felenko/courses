#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

/* Структура конфігурації симулятора Маха — Цендера */
typedef struct {
    double wavelength;  /* Довжина хвилі у метрах */
    double arm_length;  /* Довжина плеча у метрах */
    double k;           /* Хвильове число 2π/λ */
} MZM_Simulator;

/* Результати вимірювання детекторами */
typedef struct {
    double i1;          /* Інтенсивність першого детектора */
    double i2;          /* Інтенсивність другого детектора */
    double diff_signal; /* Різницевий балансний сигнал I1 - I2 */
} MZM_Result;

/* Ініціалізація параметрів симулятора */
void mzm_init(MZM_Simulator *sim, double wavelength_nm, double arm_length_mm) {
    sim->wavelength = wavelength_nm * 1e-9;
    sim->arm_length = arm_length_mm * 1e-3;
    sim->k = 2.0 * M_PI / sim->wavelength;
}

/* Симуляція одного відліку вимірювання */
MZM_Result mzm_simulate_sample(const MZM_Simulator *sim, double delta_n) {
    double phi_a = sim->k * (1.0 + delta_n) * sim->arm_length;
    double phi_b = sim->k * 1.0 * sim->arm_length;

    double inv_sqrt2 = 1.0 / sqrt(2.0);
    double complex e_in = 1.0 + 0.0 * I;

    /* Перетворення на першому світлодільнику BS1 */
    double complex e1_bs1 = e_in * inv_sqrt2;
    double complex e2_bs1 = e_in * (I * inv_sqrt2);

    /* Поширення по плечах A та B */
    double complex e1_arm = e1_bs1 * cexp(I * phi_a);
    double complex e2_arm = e2_bs1 * cexp(I * phi_b);

    /* Зведення на другому світлодільнику BS2 */
    double complex e_out1 = inv_sqrt2 * (e1_arm * I + e2_arm);
    double complex e_out2 = inv_sqrt2 * (e1_arm + e2_arm * I);

    MZM_Result res;
    res.i1 = cabs(e_out1) * cabs(e_out1);
    res.i2 = cabs(e_out2) * cabs(e_out2);
    res.diff_signal = res.i1 - res.i2;

    return res;
}

int main(void) {
    MZM_Simulator sim;
    mzm_init(&sim, 632.8, 100.0);

    printf("Чисельне моделювання інтерферометра Маха — Цендера (C99):\n");
    printf("%12s | %8s | %8s | %12s\n", "delta_n", "I1", "I2", "Diff Signal");
    printf("------------------------------------------------\n");

    for (int i = 0; i <= 10; ++i) {
        double dn = i * 1e-6;
        MZM_Result res = mzm_simulate_sample(&sim, dn);
        printf("%12.4e | %8.4f | %8.4f | %12.4f\n", dn, res.i1, res.i2, res.diff_signal);
    }

    return 0;
}
