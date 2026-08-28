#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_SAMPLE_WINDOW 128

typedef struct {
    float reference_samples[MAX_SAMPLE_WINDOW];
    float current_samples[MAX_SAMPLE_WINDOW];
    uint32_t sample_count;
    float w1_threshold_warning;
    float w1_threshold_critical;
} ShiftDetectorConfig;

typedef enum {
    SHIFT_STATUS_NOMINAL  = 0,
    SHIFT_STATUS_WARNING  = 1,
    SHIFT_STATUS_CRITICAL = 2
} ShiftDetectionStatus;

/* Допоміжна функція сортування масиву in-place (сортування вставками для малого N) */
static void insertion_sort_f32(float *arr, uint32_t n) {
    for (uint32_t i = 1; i < n; ++i) {
        float key = arr[i];
        int32_t j = (int32_t)i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

/* Розрахунок одновимірної відстані Вассерштейна W1 на статичних буферах */
float compute_wasserstein_1d(const float *ref, const float *cur, uint32_t n) {
    if (n == 0 || n > MAX_SAMPLE_WINDOW) {
        return -1.0f;
    }

    float sorted_ref[MAX_SAMPLE_WINDOW];
    float sorted_cur[MAX_SAMPLE_WINDOW];

    for (uint32_t i = 0; i < n; ++i) {
        sorted_ref[i] = ref[i];
        sorted_cur[i] = cur[i];
    }

    insertion_sort_f32(sorted_ref, n);
    insertion_sort_f32(sorted_cur, n);

    float sum_diff = 0.0f;
    for (uint32_t i = 0; i < n; ++i) {
        sum_diff += fabsf(sorted_ref[i] - sorted_cur[i]);
    }

    return sum_diff / (float)n;
}

/* Двовибірковий тест Колмогорова-Смірнова: повертає супремум різниці емпіричних CDF */
float compute_ks_statistic_1d(const float *ref, const float *cur, uint32_t n) {
    if (n == 0 || n > MAX_SAMPLE_WINDOW) {
        return -1.0f;
    }

    float s_ref[MAX_SAMPLE_WINDOW];
    float s_cur[MAX_SAMPLE_WINDOW];

    for (uint32_t i = 0; i < n; ++i) {
        s_ref[i] = ref[i];
        s_cur[i] = cur[i];
    }

    insertion_sort_f32(s_ref, n);
    insertion_sort_f32(s_cur, n);

    float d_max = 0.0f;
    uint32_t i = 0;
    uint32_t j = 0;
    const float step = 1.0f / (float)n;

    while (i < n && j < n) {
        float cdf_ref = (float)(i + 1) * step;
        float cdf_cur = (float)(j + 1) * step;

        if (s_ref[i] < s_cur[j]) {
            float diff = fabsf(cdf_ref - (float)j * step);
            if (diff > d_max) d_max = diff;
            i++;
        } else if (s_ref[i] > s_cur[j]) {
            float diff = fabsf((float)i * step - cdf_cur);
            if (diff > d_max) d_max = diff;
            j++;
        } else {
            float diff = fabsf(cdf_ref - cdf_cur);
            if (diff > d_max) d_max = diff;
            i++;
            j++;
        }
    }

    return d_max;
}

/* Оцінка стану зсуву та вибір керівного рішення безпеки */
ShiftDetectionStatus evaluate_distribution_health(
    const ShiftDetectorConfig *cfg,
    float *out_w1_distance,
    float *out_ks_stat
) {
    if (!cfg || cfg->sample_count == 0) {
        return SHIFT_STATUS_CRITICAL;
    }

    *out_w1_distance = compute_wasserstein_1d(
        cfg->reference_samples,
        cfg->current_samples,
        cfg->sample_count
    );

    *out_ks_stat = compute_ks_statistic_1d(
        cfg->reference_samples,
        cfg->current_samples,
        cfg->sample_count
    );

    if (*out_w1_distance >= cfg->w1_threshold_critical) {
        return SHIFT_STATUS_CRITICAL;
    }
    if (*out_w1_distance >= cfg->w1_threshold_warning) {
        return SHIFT_STATUS_WARNING;
    }

    return SHIFT_STATUS_NOMINAL;
}
