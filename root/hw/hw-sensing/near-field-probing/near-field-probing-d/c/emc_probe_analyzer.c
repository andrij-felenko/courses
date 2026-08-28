/* emc_probe_analyzer.c - Сканування спектра завад та аналіз гармонік (C99) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>

#define MAX_POINTS 1024
#define MAX_PEAKS 64

/* Точка калібрувальної кривої зонда (Antenna Factor) */
typedef struct {
    double freq_mhz;
    double af_db;
} ProbeCalPoint;

/* Знайдений спектральний пік */
typedef struct {
    double freq_mhz;
    double raw_dbm;
    double corrected_dbuv_m;
    bool is_over_limit;
} SpectralPeak;

/* Таблиця калібрування зонда H-Field 10 мм */
static const ProbeCalPoint PROBE_CAL[] = {
    {  10.0, 32.5 },
    {  30.0, 28.0 },
    {  50.0, 24.5 },
    { 100.0, 20.0 },
    { 200.0, 16.5 },
    { 500.0, 14.0 },
    {1000.0, 15.5 }
};
static const size_t PROBE_CAL_SIZE = sizeof(PROBE_CAL) / sizeof(PROBE_CAL[0]);

/* Лінійне інтерполювання калібрувального фактора */
double get_probe_factor(double freq_mhz) {
    if (freq_mhz <= PROBE_CAL[0].freq_mhz) return PROBE_CAL[0].af_db;
    if (freq_mhz >= PROBE_CAL[PROBE_CAL_SIZE - 1].freq_mhz)
        return PROBE_CAL[PROBE_CAL_SIZE - 1].af_db;

    for (size_t i = 0; i < PROBE_CAL_SIZE - 1; ++i) {
        if (freq_mhz >= PROBE_CAL[i].freq_mhz && freq_mhz <= PROBE_CAL[i + 1].freq_mhz) {
            double f0 = PROBE_CAL[i].freq_mhz, f1 = PROBE_CAL[i + 1].freq_mhz;
            double af0 = PROBE_CAL[i].af_db, af1 = PROBE_CAL[i + 1].af_db;
            return af0 + (af1 - af0) * (freq_mhz - f0) / (f1 - f0);
        }
    }
    return 20.0;
}

/* Перерахунок дБм у напруженість поля дБмкВ/м з урахуванням LNA та зонда */
double calculate_field_strength(double raw_dbm, double freq_mhz, double lna_gain_db) {
    double dbuv = raw_dbm + 107.0; /* 50 Ом конверсія */
    double af = get_probe_factor(freq_mhz);
    return dbuv - lna_gain_db + af;
}

/* Пошук локальних максимумів (піків), що перевищують поріг */
size_t find_peaks(const double *freqs, const double *powers_dbm, size_t count,
                  double threshold_dbm, double lna_gain, double limit_dbuv_m,
                  SpectralPeak *out_peaks, size_t max_out) {
    size_t found = 0;
    for (size_t i = 1; i < count - 1 && found < max_out; ++i) {
        if (powers_dbm[i] > powers_dbm[i - 1] &&
            powers_dbm[i] > powers_dbm[i + 1] &&
            powers_dbm[i] >= threshold_dbm) {
            out_peaks[found].freq_mhz = freqs[i];
            out_peaks[found].raw_dbm = powers_dbm[i];
            out_peaks[found].corrected_dbuv_m =
                calculate_field_strength(powers_dbm[i], freqs[i], lna_gain);
            out_peaks[found].is_over_limit =
                (out_peaks[found].corrected_dbuv_m > limit_dbuv_m);
            found++;
        }
    }
    return found;
}

/* Автоматичне визначення базової тактової частоти джерела гармонік */
double detect_fundamental_clock(const SpectralPeak *peaks, size_t peak_count) {
    if (peak_count < 2) return 0.0;
    double best_delta = 0.0;
    size_t max_matches = 0;

    for (size_t i = 0; i < peak_count - 1; ++i) {
        for (size_t j = i + 1; j < peak_count; ++j) {
            double delta = peaks[j].freq_mhz - peaks[i].freq_mhz;
            if (delta < 5.0) continue; /* ігноруємо надто близькі піки */

            size_t matches = 0;
            for (size_t k = 0; k < peak_count; ++k) {
                double remainder = fmod(peaks[k].freq_mhz + 0.5, delta);
                if (remainder < 1.0 || remainder > delta - 1.0) {
                    matches++;
                }
            }
            if (matches > max_matches) {
                max_matches = matches;
                best_delta = delta;
            }
        }
    }
    return best_delta;
}

int main(void) {
    /* Синтезований спектральний зріз тестової плати (частота 10..200 МГц) */
    double freqs[MAX_POINTS];
    double powers[MAX_POINTS];
    const size_t n_points = 380;
    const double f_start = 10.0, f_stop = 200.0;
    const double lna_gain = 20.0; /* LNA +20 дБ */
    const double cispr_limit = 40.0; /* Ліміт 40 дБмкВ/м */

    for (size_t i = 0; i < n_points; ++i) {
        freqs[i] = f_start + i * (f_stop - f_start) / (double)(n_points - 1);
        powers[i] = -85.0 + ((rand() % 100) / 50.0); /* шумова підлога ~ -85 дБм */

        /* Симуляція гармонік тактового генератора 25 МГц (Ethernet PHY) */
        for (double h = 25.0; h <= 200.0; h += 25.0) {
            if (fabs(freqs[i] - h) < 0.3) {
                powers[i] = -45.0 + (50.0 / (1.0 + (h / 50.0)));
            }
        }
    }

    SpectralPeak peaks[MAX_PEAKS];
    size_t peak_count = find_peaks(freqs, powers, n_points, -70.0,
                                   lna_gain, cispr_limit, peaks, MAX_PEAKS);

    printf("=== ЗВІТ ЗОНДУВАННЯ БЛИЖНЬОГО ПОЛЯ (NEAR-FIELD SCAN) ===\n");
    printf("Знайдено спектральних піків: %zu\n", peak_count);
    printf("%-10s | %-10s | %-16s | %-10s\n", "Частота", "Рівень", "Напруженість", "Статус");
    printf("---------------------------------------------------------\n");

    for (size_t i = 0; i < peak_count; ++i) {
        printf("%6.2f МГц | %6.1f dBm | %6.1f dBuV/m    | %s\n",
               peaks[i].freq_mhz, peaks[i].raw_dbm, peaks[i].corrected_dbuv_m,
               peaks[i].is_over_limit ? "FAIL (Перевищення!)" : "PASS");
    }

    double fundamental = detect_fundamental_clock(peaks, peak_count);
    printf("---------------------------------------------------------\n");
    printf("Ідентифікована базова тактова частота джерела: %.2f МГц\n", fundamental);
    if (fabs(fundamental - 25.0) < 1.0) {
        printf("Ймовірний винуватець: Тактовий генератор 25 МГц Ethernet PHY / USB\n");
    }

    return 0;
}
