#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Результати аналізу смуги пропускання */
typedef struct {
    double f_center;       /* Частота пикового максимуму (Гц) */
    double bw_3db;         /* Смуга за рівнем -3 дБ (Гц) */
    double bw_obw99;       /* 99% зайнята смуга ITU (Гц) */
    double f_low_3db;      /* Нижня частотна границя -3 дБ (Гц) */
    double f_high_3db;     /* Верхня частотна границя -3 дБ (Гц) */
    double f_low_obw;      /* Нижня границя 99% OBW (Гц) */
    double f_high_obw;     /* Верхня границя 99% OBW (Гц) */
} BandwidthResult;

/**
 * @brief Обчислює смугу -3 дБ та 99% OBW за масивом PSD.
 * @param psd Масив спектральної щільності потужності (лінійні одиниці Вт/Гц або V^2/Гц)
 * @param n Кількість відліків спектра (бінів БПФ)
 * @param f_start Початкова частота першого біна (Гц)
 * @param df Крок частотної сітки (Гц/бін)
 * @param res Вихідна структура для запису результатів
 * @return true у разі успішного розрахунку, false у разі помилки
 */
bool estimate_bandwidth(const double *psd, size_t n, double f_start, double df, BandwidthResult *res) {
    if (!psd || n < 3 || df <= 0.0 || !res) {
        return false;
    }

    /* 1. Знаходження максимуму та загальної інтегральної потужності */
    size_t idx_max = 0;
    double p_max = psd[0];
    double p_total = 0.0;

    for (size_t i = 0; i < n; i++) {
        p_total += psd[i];
        if (psd[i] > p_max) {
            p_max = psd[i];
            idx_max = i;
        }
    }

    if (p_max <= 1e-15 || p_total <= 1e-15) {
        return false; /* Спектр порожній або містить від'ємні значення */
    }

    res->f_center = f_start + (double)idx_max * df;
    double target_3db = p_max * 0.5; /* Рівень половинної потужності (-3.01 дБ) */

    /* 2. Пошук лівої границі -3 дБ з лінійною інтерполяцією */
    double idx_left_3db = (double)idx_max;
    for (size_t i = idx_max; i > 0; i--) {
        if (psd[i - 1] <= target_3db) {
            double p_lower = psd[i - 1];
            double p_upper = psd[i];
            double delta_p = p_upper - p_lower;
            double frac = (delta_p > 1e-12) ? (target_3db - p_lower) / delta_p : 0.0;
            idx_left_3db = (double)(i - 1) + frac;
            break;
        }
    }

    /* 3. Пошук правої границі -3 дБ з лінійною інтерполяцією */
    double idx_right_3db = (double)idx_max;
    for (size_t i = idx_max; i < n - 1; i++) {
        if (psd[i + 1] <= target_3db) {
            double p_left = psd[i];
            double p_right = psd[i + 1];
            double delta_p = p_right - p_left;
            double frac = (fabs(delta_p) > 1e-12) ? (target_3db - p_left) / delta_p : 0.0;
            idx_right_3db = (double)i + frac;
            break;
        }
    }

    res->f_low_3db = f_start + idx_left_3db * df;
    res->f_high_3db = f_start + idx_right_3db * df;
    res->bw_3db = res->f_high_3db - res->f_low_3db;

    /* 4. Пошук 99% OBW за кумулятивною інтегральною сумою */
    double lower_tail = p_total * 0.005; /* 0.5% нижнього хвоста */
    double upper_tail = p_total * 0.995; /* 99.5% повної енергії */

    double cumsum = 0.0;
    size_t idx_obw_low = 0;
    size_t idx_obw_high = n - 1;
    bool found_low = false;

    for (size_t i = 0; i < n; i++) {
        cumsum += psd[i];
        if (!found_low && cumsum >= lower_tail) {
            idx_obw_low = i;
            found_low = true;
        }
        if (cumsum >= upper_tail) {
            idx_obw_high = i;
            break;
        }
    }

    res->f_low_obw = f_start + (double)idx_obw_low * df;
    res->f_high_obw = f_start + (double)idx_obw_high * df;
    res->bw_obw99 = res->f_high_obw - res->f_low_obw;

    return true;
}

int main(void) {
    const size_t n = 512;
    double psd[512];
    double f_start = 100.0e6; /* 100 МГц несуча */
    double df = 1000.0;        /* 1 кГц на бін БПФ */

    /* Моделювання Гауссового радіосигналу з центром у 100.25 МГц */
    double center_bin = 250.0;
    double sigma_bin = 20.0;
    for (size_t i = 0; i < n; i++) {
        double diff = (double)i - center_bin;
        psd[i] = exp(-(diff * diff) / (2.0 * sigma_bin * sigma_bin));
    }

    BandwidthResult res;
    if (estimate_bandwidth(psd, n, f_start, df, &res)) {
        printf("=== Результати спектрального аналізу ===\n");
        printf("Пікова частота сигналу: %.3f МГц\n", res.f_center / 1e6);
        printf("Смуга за рівнем -3 дБ:  %.2f кГц (від %.3f до %.3f МГц)\n",
               res.bw_3db / 1e3, res.f_low_3db / 1e6, res.f_high_3db / 1e6);
        printf("Зайнята смуга 99%% OBW:  %.2f кГц (від %.3f до %.3f МГц)\n",
               res.bw_obw99 / 1e3, res.f_low_obw / 1e6, res.f_high_obw / 1e6);
    }
    return 0;
}
