#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define SHIFT_MAX_SAMPLES 64
#define SHIFT_MAX_DIM     16

typedef enum {
    SHIFT_ERR_OK = 0,
    SHIFT_ERR_INVALID_PARAM,
    SHIFT_ERR_BUFFER_NOT_FULL
} ShiftErrorCode;

typedef enum {
    SHIFT_STATUS_NOMINAL  = 0,
    SHIFT_STATUS_WARNING  = 1,
    SHIFT_STATUS_CRITICAL = 2
} ShiftSafetyStatus;

typedef struct {
    float w1_warning_threshold;
    float w1_critical_threshold;
    float mmd_warning_threshold;
    float mmd_critical_threshold;
    float rbf_gamma;
    uint32_t sample_count;
    uint32_t feature_dim;
} ShiftDetectorConfig;

typedef struct {
    float ref_samples[SHIFT_MAX_SAMPLES][SHIFT_MAX_DIM];
    float stream_ring_buffer[SHIFT_MAX_SAMPLES][SHIFT_MAX_DIM];
    uint32_t ring_head;
    uint32_t current_count;
    float cached_k_xx;
    ShiftDetectorConfig config;
    bool is_initialized;
} ShiftDetector;

typedef struct {
    float max_w1_distance;
    float max_ks_statistic;
    float mmd_squared;
    ShiftSafetyStatus safety_status;
} ShiftDiagnosticReport;

/* Внутрішнє швидке сортування масиву дійсних чисел in-place */
static void sort_f32_inplace(float *arr, int32_t left, int32_t right) {
    if (left >= right) return;
    float pivot = arr[(left + right) / 2];
    int32_t i = left;
    int32_t j = right;
    while (i <= j) {
        while (arr[i] < pivot) i++;
        while (arr[j] > pivot) j--;
        if (i <= j) {
            float tmp = arr[i];
            arr[i] = arr[j];
            arr[j] = tmp;
            i++;
            j--;
        }
    }
    if (left < j) sort_f32_inplace(arr, left, j);
    if (i < right) sort_f32_inplace(arr, i, right);
}

/* Обчислення квадрата евклідової відстані між двома векторами */
static float compute_sq_euclidean(const float *a, const float *b, uint32_t dim) {
    float sum = 0.0f;
    for (uint32_t d = 0; d < dim; ++d) {
        float diff = a[d] - b[d];
        sum += diff * diff;
    }
    return sum;
}

/* Обчислення значення RBF ядра */
static inline float compute_rbf_kernel(const float *a, const float *b, uint32_t dim, float gamma) {
    float sq_dist = compute_sq_euclidean(a, b, dim);
    return expf(-gamma * sq_dist);
}

/* Попередня генерація константи K_XX для еталонного датасету */
static float precompute_k_xx(const float ref[SHIFT_MAX_SAMPLES][SHIFT_MAX_DIM], uint32_t n, uint32_t dim, float gamma) {
    if (n < 2) return 0.0f;
    float sum = 0.0f;
    for (uint32_t i = 0; i < n; ++i) {
        for (uint32_t j = 0; j < n; ++j) {
            if (i != j) {
                sum += compute_rbf_kernel(ref[i], ref[j], dim, gamma);
            }
        }
    }
    return sum / (float)(n * (n - 1));
}

/* Ініціалізація детектора зсуву */
ShiftErrorCode shift_detector_init(
    ShiftDetector *detector,
    const ShiftDetectorConfig *config,
    const float ref_data[SHIFT_MAX_SAMPLES][SHIFT_MAX_DIM]
) {
    if (!detector || !config || !ref_data) {
        return SHIFT_ERR_INVALID_PARAM;
    }
    if (config->sample_count == 0 || config->sample_count > SHIFT_MAX_SAMPLES ||
        config->feature_dim == 0 || config->feature_dim > SHIFT_MAX_DIM ||
        config->rbf_gamma <= 0.0f) {
        return SHIFT_ERR_INVALID_PARAM;
    }

    memset(detector, 0, sizeof(ShiftDetector));
    detector->config = *config;

    for (uint32_t i = 0; i < config->sample_count; ++i) {
        for (uint32_t d = 0; d < config->feature_dim; ++d) {
            detector->ref_samples[i][d] = ref_data[i][d];
        }
    }

    detector->cached_k_xx = precompute_k_xx(
        detector->ref_samples,
        config->sample_count,
        config->feature_dim,
        config->rbf_gamma
    );

    detector->ring_head = 0;
    detector->current_count = 0;
    detector->is_initialized = true;

    return SHIFT_ERR_OK;
}

/* Додавання нового вектора вимірювання у кільцевий буфер реального часу */
ShiftErrorCode shift_detector_push_sample(ShiftDetector *detector, const float *sample_vector) {
    if (!detector || !detector->is_initialized || !sample_vector) {
        return SHIFT_ERR_INVALID_PARAM;
    }

    uint32_t head = detector->ring_head;
    uint32_t dim = detector->config.feature_dim;

    for (uint32_t d = 0; d < dim; ++d) {
        detector->stream_ring_buffer[head][d] = sample_vector[d];
    }

    detector->ring_head = (head + 1) % detector->config.sample_count;
    if (detector->current_count < detector->config.sample_count) {
        detector->current_count++;
    }

    return SHIFT_ERR_OK;
}

/* Обчислення одновимірної відстані Вассерштейна для заданого каналу ознак */
float shift_detector_calc_w1_channel(
    const ShiftDetector *detector,
    uint32_t channel_idx
) {
    if (!detector || channel_idx >= detector->config.feature_dim) {
        return -1.0f;
    }

    uint32_t n = detector->config.sample_count;
    float s_ref[SHIFT_MAX_SAMPLES];
    float s_cur[SHIFT_MAX_SAMPLES];

    for (uint32_t i = 0; i < n; ++i) {
        s_ref[i] = detector->ref_samples[i][channel_idx];
        s_cur[i] = detector->stream_ring_buffer[i][channel_idx];
    }

    sort_f32_inplace(s_ref, 0, (int32_t)n - 1);
    sort_f32_inplace(s_cur, 0, (int32_t)n - 1);

    float sum_diff = 0.0f;
    for (uint32_t i = 0; i < n; ++i) {
        sum_diff += fabsf(s_ref[i] - s_cur[i]);
    }

    return sum_diff / (float)n;
}

/* Обчислення статистики Колмогорова-Смірнова для заданого каналу */
float shift_detector_calc_ks_channel(
    const ShiftDetector *detector,
    uint32_t channel_idx
) {
    if (!detector || channel_idx >= detector->config.feature_dim) {
        return -1.0f;
    }

    uint32_t n = detector->config.sample_count;
    float s_ref[SHIFT_MAX_SAMPLES];
    float s_cur[SHIFT_MAX_SAMPLES];

    for (uint32_t i = 0; i < n; ++i) {
        s_ref[i] = detector->ref_samples[i][channel_idx];
        s_cur[i] = detector->stream_ring_buffer[i][channel_idx];
    }

    sort_f32_inplace(s_ref, 0, (int32_t)n - 1);
    sort_f32_inplace(s_cur, 0, (int32_t)n - 1);

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

/* Розрахунок незміщеної квадратичної MMD між еталоном і поточним буфером */
float shift_detector_calc_mmd_squared(const ShiftDetector *detector) {
    if (!detector || detector->current_count < detector->config.sample_count) {
        return -1.0f;
    }

    uint32_t n = detector->config.sample_count;
    uint32_t dim = detector->config.feature_dim;
    float gamma = detector->config.rbf_gamma;

    /* 1. Розрахунок перехресної взаємодії K_XY */
    float sum_xy = 0.0f;
    for (uint32_t i = 0; i < n; ++i) {
        for (uint32_t j = 0; j < n; ++j) {
            sum_xy += compute_rbf_kernel(
                detector->ref_samples[i],
                detector->stream_ring_buffer[j],
                dim,
                gamma
            );
        }
    }
    float k_xy = sum_xy / (float)(n * n);

    /* 2. Розрахунок внутрішньої взаємодії потоку K_YY */
    float sum_yy = 0.0f;
    for (uint32_t i = 0; i < n; ++i) {
        for (uint32_t j = 0; j < n; ++j) {
            if (i != j) {
                sum_yy += compute_rbf_kernel(
                    detector->stream_ring_buffer[i],
                    detector->stream_ring_buffer[j],
                    dim,
                    gamma
                );
            }
        }
    }
    float k_yy = sum_yy / (float)(n * (n - 1));

    /* 3. Підсумкова незміщена оцінка: MMD² = K_XX - 2*K_XY + K_YY */
    float mmd2 = detector->cached_k_xx - 2.0f * k_xy + k_yy;
    return (mmd2 > 0.0f) ? mmd2 : 0.0f;
}

/* Комплексний аудит стану розподілу та визначення статусу безпеки */
ShiftErrorCode shift_detector_evaluate(
    const ShiftDetector *detector,
    ShiftDiagnosticReport *report
) {
    if (!detector || !report || !detector->is_initialized) {
        return SHIFT_ERR_INVALID_PARAM;
    }
    if (detector->current_count < detector->config.sample_count) {
        return SHIFT_ERR_BUFFER_NOT_FULL;
    }

    float max_w1 = 0.0f;
    float max_ks = 0.0f;

    for (uint32_t d = 0; d < detector->config.feature_dim; ++d) {
        float w1 = shift_detector_calc_w1_channel(detector, d);
        float ks = shift_detector_calc_ks_channel(detector, d);
        if (w1 > max_w1) max_w1 = w1;
        if (ks > max_ks) max_ks = ks;
    }

    float mmd2 = shift_detector_calc_mmd_squared(detector);

    report->max_w1_distance = max_w1;
    report->max_ks_statistic = max_ks;
    report->mmd_squared = mmd2;

    if (mmd2 >= detector->config.mmd_critical_threshold ||
        max_w1 >= detector->config.w1_critical_threshold) {
        report->safety_status = SHIFT_STATUS_CRITICAL;
    } else if (mmd2 >= detector->config.mmd_warning_threshold ||
               max_w1 >= detector->config.w1_warning_threshold) {
        report->safety_status = SHIFT_STATUS_WARNING;
    } else {
        report->safety_status = SHIFT_STATUS_NOMINAL;
    }

    return SHIFT_ERR_OK;
}
