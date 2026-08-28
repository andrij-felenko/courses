#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double l_zero;        /* Номінальна початкова індуктивність L_0, Гн */
    double i_sat_10;      /* Струм при падінні L на 10% (0.90 * L_0), А */
    double i_sat_20;      /* Струм при падінні L на 20% (0.80 * L_0), А */
    double i_sat_30;      /* Струм при падінні L на 30% (0.70 * L_0), А */
    double energy_max_j;  /* Повна енергія магнітного поля, Дж */
    bool is_valid;
} InductorAnalysisResult;

/*
 * Обробка імпульсних осцилограм дроселя.
 * v_raw: масив напруги на дроселі (В)
 * i_raw: масив струму (А)
 * n: кількість точок вимірювання (не менше 10)
 * dt: крок дискретизації часу (с)
 * r_dc: активний опір обмотки (Ом)
 * l_diff_out: вихідний масив диференціальної індуктивності (розмір n)
 * psi_out: вихідний масив потокозчеплення (розмір n)
 */
InductorAnalysisResult process_saturation_curve(
    const double *v_raw,
    const double *i_raw,
    size_t n,
    double dt,
    double r_dc,
    double *l_diff_out,
    double *psi_out
) {
    InductorAnalysisResult res = {0.0, 0.0, 0.0, 0.0, 0.0, false};
    if (!v_raw || !i_raw || !l_diff_out || !psi_out || n < 10 || dt <= 0.0) {
        return res;
    }

    /* 1. Чисельне інтегрування потокозчеплення Psi(t) за правилом трапецій */
    psi_out[0] = 0.0;
    double total_energy = 0.0;

    for (size_t k = 1; k < n; ++k) {
        double e_prev = v_raw[k - 1] - i_raw[k - 1] * r_dc;
        double e_curr = v_raw[k] - i_raw[k] * r_dc;
        double d_psi = 0.5 * (e_prev + e_curr) * dt;
        psi_out[k] = psi_out[k - 1] + d_psi;

        /* Накопичення енергії поля: W = integral(i * dPsi) */
        double avg_i = 0.5 * (i_raw[k - 1] + i_raw[k]);
        total_energy += avg_i * d_psi;
    }
    res.energy_max_j = total_energy;

    /* 2. Обчислення похідної струму di/dt фільтром Савицького-Голея (5 точок) */
    l_diff_out[0] = 0.0;
    l_diff_out[1] = 0.0;
    l_diff_out[n - 2] = 0.0;
    l_diff_out[n - 1] = 0.0;

    for (size_t k = 2; k < n - 2; ++k) {
        double didt = (-2.0 * i_raw[k - 2] - 1.0 * i_raw[k - 1] +
                        1.0 * i_raw[k + 1] + 2.0 * i_raw[k + 2]) / (10.0 * dt);
        double e_ind = v_raw[k] - i_raw[k] * r_dc;

        if (didt > 1e2 && e_ind > 0.0) {
            l_diff_out[k] = e_ind / didt;
        } else {
            l_diff_out[k] = (k > 2) ? l_diff_out[k - 1] : 0.0;
        }
    }

    /* 3. Оцінка початкової індуктивності L_0 у стабільному діапазоні (перші 15% точок) */
    size_t start_idx = 2;
    size_t end_idx = n / 7;
    if (end_idx <= start_idx + 2) end_idx = start_idx + 3;
    if (end_idx >= n - 2) end_idx = n - 3;

    double l_sum = 0.0;
    size_t count = 0;
    for (size_t k = start_idx; k <= end_idx; ++k) {
        if (l_diff_out[k] > 0.0) {
            l_sum += l_diff_out[k];
            count++;
        }
    }

    if (count == 0) return res;
    res.l_zero = l_sum / (double)count;

    /* 4. Пошук порогових струмів насичення I_sat_10, I_sat_20, I_sat_30 */
    double th_10 = res.l_zero * 0.90;
    double th_20 = res.l_zero * 0.80;
    double th_30 = res.l_zero * 0.70;

    bool f10 = false, f20 = false, f30 = false;

    for (size_t k = end_idx; k < n - 2; ++k) {
        if (!f10 && l_diff_out[k] <= th_10 && l_diff_out[k] > 0.0) {
            res.i_sat_10 = i_raw[k];
            f10 = true;
        }
        if (!f20 && l_diff_out[k] <= th_20 && l_diff_out[k] > 0.0) {
            res.i_sat_20 = i_raw[k];
            f20 = true;
        }
        if (!f30 && l_diff_out[k] <= th_30 && l_diff_out[k] > 0.0) {
            res.i_sat_30 = i_raw[k];
            f30 = true;
            break;
        }
    }

    res.is_valid = f10;
    return res;
}
