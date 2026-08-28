#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

// Статуси класифікації кристала
typedef enum {
    DIE_STATUS_PASS,             // Повністю придатний кристал
    DIE_STATUS_OUTLIER_REJECT,   // Статистичний викид за PAT (прихований дефект)
    DIE_STATUS_HARD_REJECT       // Грубий брак (вихід за межі даташита)
} die_status_t;

// Структура конфігурації специфікації даташита
typedef struct {
    double lsl;                 // Нижня межа специфікації даташита
    double usl;                 // Верхня межа специфікації даташита
    double sigma_multiplier;    // Коефіцієнт відсікання PAT (типово 3.0 або 4.0)
} pat_spec_t;

// Структура розрахованих статистичних меж
typedef struct {
    double mean;                // Вибіркове середнє партії
    double std_dev;             // Стандартне відхилення партії
    double dynamic_lsl;         // Динамічна нижня межа PAT
    double dynamic_usl;         // Динамічна верхня межа PAT
} pat_limits_t;

// Обчислення середнього та стандартного відхилення
bool calculate_sample_stats(const double* data, size_t count, double* out_mean, double* out_std) {
    if (data == NULL || count < 2 || out_mean == NULL || out_std == NULL) {
        return false;
    }

    double sum = 0.0;
    for (size_t i = 0; i < count; ++i) {
        sum += data[i];
    }
    double mean = sum / (double)count;

    double sum_sq_diff = 0.0;
    for (size_t i = 0; i < count; ++i) {
        double diff = data[i] - mean;
        sum_sq_diff += diff * diff;
    }
    double std_dev = sqrt(sum_sq_diff / (double)(count - 1));

    *out_mean = mean;
    *out_std = std_dev;
    return true;
}

// Розрахунок адаптивних меж PAT
bool compute_pat_limits(const double* data, size_t count, const pat_spec_t* spec, pat_limits_t* out_limits) {
    if (spec == NULL || out_limits == NULL) {
        return false;
    }

    double mean = 0.0;
    double std_dev = 0.0;
    if (!calculate_sample_stats(data, count, &mean, &std_dev)) {
        return false;
    }

    out_limits->mean = mean;
    out_limits->std_dev = std_dev;

    // Розрахунок динамічних порогів
    double raw_dyn_lsl = mean - (spec->sigma_multiplier * std_dev);
    double raw_dyn_usl = mean + (spec->sigma_multiplier * std_dev);

    // Затискання динамічних меж паспортними рамками даташита
    out_limits->dynamic_lsl = (raw_dyn_lsl > spec->lsl) ? raw_dyn_lsl : spec->lsl;
    out_limits->dynamic_usl = (raw_dyn_usl < spec->usl) ? raw_dyn_usl : spec->usl;

    return true;
}

// Класифікація одиничного кристала за розрахованими межами
die_status_t classify_die(double value, const pat_spec_t* spec, const pat_limits_t* limits) {
    // 1. Перевірка на грубий вихід за паспортні рамки даташита
    if (value < spec->lsl || value > spec->usl) {
        return DIE_STATUS_HARD_REJECT;
    }

    // 2. Перевірка на вихід за динамічні статистичні межі PAT
    if (value < limits->dynamic_lsl || value > limits->dynamic_usl) {
        return DIE_STATUS_OUTLIER_REJECT;
    }

    return DIE_STATUS_PASS;
}

int main(void) {
    // Специфікація даташита для струму спокою операційного підсилювача (мкА)
    // Номінал: 100 мкА, межі даташита: Min = 80 мкА, Max = 120 мкА
    const pat_spec_t spec = {
        .lsl = 80.0,
        .usl = 120.0,
        .sigma_multiplier = 3.0
    };

    // Масив вимірювань вибірки з 12 кристалів однієї кремнієвої пластини
    // Зразок #10 (114.0 мкА) формально вкладається в ліміт 120 мкА, але є аномалією
    const double wafer_measurements[] = {
        99.2, 100.5, 98.8, 101.1, 99.7, 100.2,
        98.9, 100.8, 99.4, 114.0, 100.1, 125.5
    };
    const size_t count = sizeof(wafer_measurements) / sizeof(wafer_measurements[0]);

    pat_limits_t limits;
    if (!compute_pat_limits(wafer_measurements, count, &spec, &limits)) {
        fprintf(stderr, "Помилка обчислення меж PAT\n");
        return 1;
    }

    printf("=== Статистика вибірки пластини (AEC-Q001 PAT) ===\n");
    printf("Середнє (Mean):       %.3f мкА\n", limits.mean);
    printf("Стандартне відхилення: %.3f мкА\n", limits.std_dev);
    printf("Межі даташита:        [%.1f ... %.1f] мкА\n", spec.lsl, spec.usl);
    printf("Динамічні межі PAT:   [%.3f ... %.3f] мкА\n\n", limits.dynamic_lsl, limits.dynamic_usl);

    printf("Результати класифікації кристалів:\n");
    for (size_t i = 0; i < count; ++i) {
        double val = wafer_measurements[i];
        die_status_t status = classify_die(val, &spec, &limits);

        const char* status_str = "";
        switch (status) {
            case DIE_STATUS_PASS:
                status_str = "ПРИДАТНИЙ (PASS)";
                break;
            case DIE_STATUS_OUTLIER_REJECT:
                status_str = "БРАК PAT (OUTLIER - прихований дефект!)";
                break;
            case DIE_STATUS_HARD_REJECT:
                status_str = "БРАК ДАТАШИТА (HARD REJECT)";
                break;
        }

        printf("  Чіп #%02zu: %6.2f мкА -> %s\n", i + 1, val, status_str);
    }

    return 0;
}
