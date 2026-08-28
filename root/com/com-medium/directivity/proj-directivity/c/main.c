#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура результату розрахунку спрямованості
typedef struct {
    double directivity_linear; // D (лінійне значення)
    double directivity_dbi;    // D_dBi (у dBi)
    double p_rad_watts;        // Повна випромінена потужність (Вт)
    double u_max;              // Максимальна інтенсивність (Вт/ст)
    double hpbw_theta_deg;     // Ширина променя в E-площині (градуси)
    double hpbw_phi_deg;       // Ширина променя в H-площині (градуси)
} antenna_directivity_t;

// Обчислення спрямованості методом трапецій по сферичній сітці U(theta, phi)
// theta_steps: кількість кроків по куту θ (0..π)
// phi_steps: кількість кроків по куту ϕ (0..2π)
// grid: плоский масив розміром (theta_steps + 1) * (phi_steps + 1)
antenna_directivity_t calculate_directivity_c(
    const double *grid,
    int theta_steps,
    int phi_steps)
{
    antenna_directivity_t res = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    if (!grid || theta_steps < 2 || phi_steps < 2) return res;

    double d_theta = M_PI / theta_steps;
    double d_phi = (2.0 * M_PI) / phi_steps;

    double u_max = 0.0;
    double p_rad = 0.0;

    // Крок 1: Пошук максимуму для визначення порогу шуму
    for (int i = 0; i <= theta_steps; ++i) {
        for (int j = 0; j < phi_steps; ++j) {
            double u_val = grid[i * (phi_steps + 1) + j];
            if (u_val > u_max) u_max = u_val;
        }
    }

    // Поріг шуму -40 дБ від максимуму
    double noise_floor = u_max * 1e-4;

    // Крок 2: Чисельне інтегрування трапеціями
    for (int i = 0; i <= theta_steps; ++i) {
        double theta = i * d_theta;
        double sin_theta = sin(theta);
        // Вага трапеції по θ: 0.5 на крайніх точках, 1.0 всередині
        double w_theta = (i == 0 || i == theta_steps) ? 0.5 : 1.0;

        for (int j = 0; j < phi_steps; ++j) {
            int idx = i * (phi_steps + 1) + j;
            double u_val = grid[idx];

            // Відсікання вимірювального шуму нижче порогу
            if (u_val < noise_floor) u_val = 0.0;

            p_rad += u_val * sin_theta * w_theta;
        }
    }

    p_rad *= (d_theta * d_phi);

    if (p_rad > 1e-15 && u_max > 0.0) {
        res.u_max = u_max;
        res.p_rad_watts = p_rad;
        res.directivity_linear = (4.0 * M_PI * u_max) / p_rad;
        res.directivity_dbi = 10.0 * log10(res.directivity_linear);
    }

    return res;
}

// Допоміжна функція оцінки HPBW по головних зрізах
void estimate_hpbw_c(
    const double *grid,
    int theta_steps,
    int phi_steps,
    double u_max,
    double *out_hpbw_theta,
    double *out_hpbw_phi)
{
    *out_hpbw_theta = 0.0;
    *out_hpbw_phi = 0.0;
    if (u_max <= 0.0) return;

    double target = 0.5 * u_max;
    double d_theta_deg = 180.0 / theta_steps;

    // Пошук точок -3 дБ вздовж головного зрізу ϕ = 0
    int idx_max_theta = 0;
    for (int i = 0; i <= theta_steps; ++i) {
        if (grid[i * (phi_steps + 1)] >= u_max * 0.999) {
            idx_max_theta = i;
            break;
        }
    }

    int i_left = idx_max_theta;
    while (i_left > 0 && grid[i_left * (phi_steps + 1)] > target) {
        i_left--;
    }

    int i_right = idx_max_theta;
    while (i_right < theta_steps && grid[i_right * (phi_steps + 1)] > target) {
        i_right++;
    }

    *out_hpbw_theta = (i_right - i_left) * d_theta_deg;
    *out_hpbw_phi = *out_hpbw_theta; // Спрощено для симетричного променя
}

int main(void) {
    int theta_steps = 180; // крок 1 градус
    int phi_steps = 360;   // крок 1 градус
    int total_points = (theta_steps + 1) * (phi_steps + 1);

    double *grid = (double *)malloc(sizeof(double) * total_points);
    if (!grid) return 1;

    // Синтетична діаграма випромінювання диполя U(θ) = sin²(θ)
    for (int i = 0; i <= theta_steps; ++i) {
        double theta = i * (M_PI / theta_steps);
        double val = sin(theta) * sin(theta);
        for (int j = 0; j <= phi_steps; ++j) {
            grid[i * (phi_steps + 1) + j] = val;
        }
    }

    antenna_directivity_t res = calculate_directivity_c(grid, theta_steps, phi_steps);
    estimate_hpbw_c(grid, theta_steps, phi_steps, res.u_max, &res.hpbw_theta_deg, &res.hpbw_phi_deg);

    printf("--- Тест півхвильового диполя (C) ---\n");
    printf("U_max    = %.4f Вт/ст\n", res.u_max);
    printf("P_rad    = %.4f Вт\n", res.p_rad_watts);
    printf("D_linear = %.4f (теоретичне: 1.6400)\n", res.directivity_linear);
    printf("D_dBi    = %.2f dBi (теоретичне: 2.15 dBi)\n", res.directivity_dbi);
    printf("HPBW_θ   = %.1f градусів\n", res.hpbw_theta_deg);

    free(grid);
    return 0;
}
