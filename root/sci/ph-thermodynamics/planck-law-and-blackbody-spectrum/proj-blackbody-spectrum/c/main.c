#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Фундаментальні фізичні константи в системі SI (CODATA 2018) */
#define CONST_H  6.62607015e-34  /* Стала Планка (Дж·с) */
#define CONST_C  2.99792458e8    /* Швидкість світла (м/с) */
#define CONST_KB 1.380649e-23    /* Стала Больцмана (Дж/К) */
#define CONST_SIGMA 5.670374e-8  /* Стала Стефана-Больцмана (Вт/(м²·К⁴)) */

/* 
 * Спектральна яскравість Планка B_λ(λ, T)
 * λ — довжина хвилі у метрах
 * T — температура у Кельвінах
 * Повертає значення у Вт / (м² · ст · м)
 */
double planck_spectral_radiance(double lambda, double T) {
    if (lambda <= 0.0 || T <= 0.0) {
        return 0.0;
    }

    const double c1 = 2.0 * CONST_H * CONST_C * CONST_C; /* 2 h c² */
    const double c2 = (CONST_H * CONST_C) / CONST_KB;    /* h c / k_B */

    double x = c2 / (lambda * T);

    /* Захист від переповнення експоненти при дуже малих λ */
    if (x > 700.0) {
        return 0.0;
    }

    /* Захист від втрати точності при малих x за допомогою expm1 */
    double denom = expm1(x);
    if (denom <= 0.0) {
        return 0.0;
    }

    double lambda5 = lambda * lambda * lambda * lambda * lambda;
    return c1 / (lambda5 * denom);
}

/* 
 * Чисельне інтегрування спектральної яскравості за правилом Сімпсона
 * Повертає інтегральну яскравість (Вт / (м² · ст))
 */
double integrate_radiance_simpson(double T, double lambda_start, double lambda_end, int num_intervals) {
    if (num_intervals % 2 != 0) {
        num_intervals++; /* Правило Сімпсона вимагає парної кількості інтервалів */
    }

    double h = (lambda_end - lambda_start) / num_intervals;
    double sum = planck_spectral_radiance(lambda_start, T) + planck_spectral_radiance(lambda_end, T);

    for (int i = 1; i < num_intervals; i++) {
        double lambda = lambda_start + i * h;
        double val = planck_spectral_radiance(lambda, T);
        if (i % 2 == 0) {
            sum += 2.0 * val;
        } else {
            sum += 4.0 * val;
        }
    }

    return (h / 3.0) * sum;
}

/* 
 * Пошук довжини хвилі максимуму спектра (Закон Віна) методом бісекції
 */
double find_wien_peak_bisection(double T, double tol) {
    double low = 1.0e-9;
    double high = 1.0e-3;

    /* Використовуємо похідну за λ через скінченні різниці */
    while ((high - low) > tol) {
        double mid = low + (high - low) / 2.0;
        double delta = mid * 1.0e-5;

        double b_plus = planck_spectral_radiance(mid + delta, T);
        double b_minus = planck_spectral_radiance(mid - delta, T);
        double deriv = (b_plus - b_minus) / (2.0 * delta);

        if (deriv > 0.0) {
            low = mid;
        } else {
            high = mid;
        }
    }

    return (low + high) / 2.0;
}

int main(void) {
    double T = 5778.0; /* Ефективна температура поверхні Сонця (K) */
    printf("--- Симуляція випромінювання чорного тіла (C) ---\n");
    printf("Температура: %.1f K\n", T);

    double lambda_peak = find_wien_peak_bisection(T, 1.0e-12);
    printf("Чисельний пік Віна λ_max: %.3f нм (Теоретичний: %.3f нм)\n",
           lambda_peak * 1.0e9, (2.8977719e-3 / T) * 1.0e9);

    /* Інтегруємо від 10 нм до 10 мкм */
    double integrated_b = integrate_radiance_simpson(T, 1.0e-8, 1.0e-5, 10000);
    double total_emittance = M_PI * integrated_b; /* j* = π · B_total */
    double theoretical_emittance = CONST_SIGMA * pow(T, 4.0);

    printf("Обчислена випромінювальна здатність: %.3e Вт/м²\n", total_emittance);
    printf("Теоретична (Стефан-Больцман):         %.3e Вт/м²\n", theoretical_emittance);
    printf("Відносна похибка:                     %.4f%%\n",
           fabs(total_emittance - theoretical_emittance) / theoretical_emittance * 100.0);

    return 0;
}
