#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define DTOF_HIST_BINS      64
#define SPEED_OF_LIGHT_M_S  299792458.0

typedef struct {
    double bin_width_ps;       /* часова ширина одного біна гістограми, пс */
    uint32_t total_cycles;     /* загальна кількість лазерних пострілів */
    double distance_m;         /* обчислена відстань до об'єкта, метри */
    double confidence;         /* коефіцієнт достовірності / відношення сигнал/шум */
    bool valid;                /* прапорець успішного виявлення піка */
} dtof_result_t;

/* Обробка сирої гістограми dToF: компенсація нагромадження, фільтрація та центроїд */
dtof_result_t process_dtof_histogram(const uint32_t *raw_hist, size_t num_bins,
                                    double bin_width_ps, uint32_t total_cycles) {
    dtof_result_t res;
    res.bin_width_ps = bin_width_ps;
    res.total_cycles = total_cycles;
    res.distance_m = 0.0;
    res.confidence = 0.0;
    res.valid = false;

    if (num_bins == 0 || num_bins > DTOF_HIST_BINS || total_cycles == 0) {
        return res;
    }

    double corr_hist[DTOF_HIST_BINS];
    uint32_t cumulative_events = 0;

    /* 1. Статистична пуассонівська корекція нагромадження (Coates correction) */
    for (size_t i = 0; i < num_bins; ++i) {
        int64_t available_cycles = (int64_t)total_cycles - (int64_t)cumulative_events;
        if (available_cycles <= (int64_t)raw_hist[i] || available_cycles <= 0) {
            corr_hist[i] = (double)raw_hist[i];
        } else {
            double p = (double)raw_hist[i] / (double)available_cycles;
            if (p >= 0.999) p = 0.999;
            corr_hist[i] = -((double)total_cycles) * log(1.0 - p);
        }
        cumulative_events += raw_hist[i];
    }

    /* 2. Оцінка рівня сонячного шуму (за першими та останніми 8 бінами) */
    double noise_sum = 0.0;
    size_t noise_count = 0;
    for (size_t i = 0; i < 8 && i < num_bins; ++i) {
        noise_sum += corr_hist[i];
        noise_count++;
    }
    for (size_t i = (num_bins > 8 ? num_bins - 8 : 0); i < num_bins; ++i) {
        noise_sum += corr_hist[i];
        noise_count++;
    }
    double noise_floor = (noise_count > 0) ? (noise_sum / (double)noise_count) : 0.0;

    /* 3. Віднімання фону та пошук індексу максимуму піка */
    double max_signal = 0.0;
    size_t peak_idx = 0;

    for (size_t i = 0; i < num_bins; ++i) {
        corr_hist[i] = fmax(0.0, corr_hist[i] - noise_floor);
        if (corr_hist[i] > max_signal) {
            max_signal = corr_hist[i];
            peak_idx = i;
        }
    }

    /* Поріг детекції: пік має перевищувати шум щонайменше в 3 рази */
    double min_threshold = fmax(10.0, sqrt(noise_floor + 1.0) * 3.5);
    if (max_signal < min_threshold || peak_idx == 0 || peak_idx >= num_bins - 1) {
        return res; /* пік відсутній або за межами діапазону */
    }

    /* 4. Суб-біновий розрахунок центроїда піка (3-точковий центр мас) */
    double w_left   = corr_hist[peak_idx - 1];
    double w_center = corr_hist[peak_idx];
    double w_right  = corr_hist[peak_idx + 1];
    double weight_sum = w_left + w_center + w_right;

    if (weight_sum <= 0.0) {
        return res;
    }

    double sub_bin_offset = (w_right - w_left) / weight_sum;
    double exact_bin = (double)peak_idx + sub_bin_offset;

    /* 5. Перерахунок часу прольоту в метри */
    double tof_seconds = exact_bin * (bin_width_ps * 1e-12);
    res.distance_m = (SPEED_OF_LIGHT_M_S * tof_seconds) / 2.0;
    res.confidence = max_signal / (noise_floor + 1.0);
    res.valid = true;

    return res;
}
