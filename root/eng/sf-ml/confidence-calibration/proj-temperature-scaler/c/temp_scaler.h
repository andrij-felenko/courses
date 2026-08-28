/* ============================================================================
 * Файл: temp_scaler.h
 * Опис: Інженерний модуль калібрування впевненості логітів нейромережі (C99)
 * ============================================================================ */
#ifndef TEMP_SCALER_H
#define TEMP_SCALER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define TS_MAX_CLASSES 128
#define TS_MAX_BINS 64

/* Коди повернення та помилок модуля */
typedef enum {
    TS_SUCCESS = 0,
    TS_ERR_INVALID_PARAM = -1,
    TS_ERR_BUFFER_OVERFLOW = -2,
    TS_ERR_NUMERICAL_INSTABILITY = -3,
    TS_ERR_OPTIMIZATION_FAILED = -4
} ts_status_t;

/* Структура результату порогового прийняття рішення */
typedef struct {
    size_t predicted_class;
    float calibrated_confidence;
    bool is_safe_to_execute;
} ts_decision_t;

/* Структура метрик якості калібрування */
typedef struct {
    float ece;          /* Expected Calibration Error */
    float mce;          /* Maximum Calibration Error */
    float brier_score;  /* Середній бал Браєра */
    float nll;          /* Середня негативна лог-правдоподібність */
} ts_metrics_t;

/* Структура набору валідаційних даних для калібрування */
typedef struct {
    const float* logits_flat; /* Плаский масив логітів: розмір num_samples * num_classes */
    const size_t* labels;     /* Масив істинних міток класів: розмір num_samples */
    size_t num_samples;       /* Кількість валідаційних зразків */
    size_t num_classes;       /* Кількість класів */
} ts_dataset_t;

/* Основні функції калібрувальника */

/**
 * @brief Чисельно стабільне масштабування логітів температурою та обчислення Softmax
 * @param logits Вхідний масив сирих логітів
 * @param num_classes Кількість класів (розмір масиву logits)
 * @param temperature Скалярна температура T (повинна бути > 0.0f)
 * @param out_probs Вихідний масив відкаліброваних імовірностей (розмір num_classes)
 * @return TS_SUCCESS при успішному завершенні або код помилки
 */
ts_status_t ts_calibrate_logits(const float* logits, size_t num_classes, 
                               float temperature, float* out_probs);

/**
 * @brief Порогова оцінка рішення з перевіркою безпеки
 * @param logits Вхідний масив логітів
 * @param num_classes Кількість класів
 * @param temperature Скалярна температура T
 * @param safety_threshold Поріг впевненості для виконання автономної дії [0.0, 1.0]
 * @param out_decision Покажчик на структуру результату рішення
 * @return TS_SUCCESS при успішному завершенні або код помилки
 */
ts_status_t ts_evaluate_safety(const float* logits, size_t num_classes, 
                              float temperature, float safety_threshold,
                              ts_decision_t* out_decision);

/**
 * @brief Розрахунок метрик калібрування (ECE, MCE, NLL, Brier) на тестовому наборі
 * @param dataset Валідаційний або тестовий набір даних
 * @param temperature Скалярна температура T
 * @param num_bins Кількість бінів для розрахунку ECE/MCE (типово 15)
 * @param out_metrics Покажчик на структуру метрик
 * @return TS_SUCCESS при успішному завершенні або код помилки
 */
ts_status_t ts_compute_metrics(const ts_dataset_t* dataset, float temperature,
                              size_t num_bins, ts_metrics_t* out_metrics);

/**
 * @brief Оптимізація температури T на калібрувальному наборі методом золотого перетину
 * @param dataset Калібрувальний набір валідаційних даних
 * @param min_temp Мінімальна межа пошуку температури (наприклад, 0.1f)
 * @param max_temp Максимальна межа пошуку температури (наприклад, 10.0f)
 * @param max_iterations Максимальна кількість ітерацій (типово 35)
 * @param tolerance Допустима похибка зупинки пошуку (наприклад, 1e-5f)
 * @param out_optimal_temperature Покажчик на результуюче значення T*
 * @return TS_SUCCESS при успішному завершенні або код помилки
 */
ts_status_t ts_optimize_temperature(const ts_dataset_t* dataset, 
                                   float min_temp, float max_temp,
                                   size_t max_iterations, float tolerance,
                                   float* out_optimal_temperature);

#ifdef __cplusplus
/* ============================================================================
 * Файл: temp_scaler.c
 * Опис: Реалізація функцій обчислення калібрування та оптимізації температури
 * ============================================================================ */
#include <math.h>
#include <float.h>

ts_status_t ts_calibrate_logits(const float* logits, size_t num_classes, 
                               float temperature, float* out_probs) {
    if (!logits || !out_probs || num_classes == 0 || temperature <= 0.0f || isnan(temperature)) {
        return TS_ERR_INVALID_PARAM;
    }

    const float inv_t = 1.0f / temperature;

    /* 1. Пошук максимуму для запобігання переповненню експоненти */
    float max_scaled = logits[0] * inv_t;
    for (size_t i = 1; i < num_classes; ++i) {
        float scaled = logits[i] * inv_t;
        if (scaled > max_scaled) {
            max_scaled = scaled;
        }
    }

    if (isnan(max_scaled) || isinf(max_scaled)) {
        return TS_ERR_NUMERICAL_INSTABILITY;
    }

    /* 2. Обчислення експонент */
    float sum_exp = 0.0f;
    for (size_t i = 0; i < num_classes; ++i) {
        float e = expf(logits[i] * inv_t - max_scaled);
        out_probs[i] = e;
        sum_exp += e;
    }

    if (sum_exp <= 0.0f || isnan(sum_exp) || isinf(sum_exp)) {
        return TS_ERR_NUMERICAL_INSTABILITY;
    }

    /* 3. Нормалізація розподілу */
    const float inv_sum = 1.0f / sum_exp;
    for (size_t i = 0; i < num_classes; ++i) {
        out_probs[i] *= inv_sum;
    }

    return TS_SUCCESS;
}

ts_status_t ts_evaluate_safety(const float* logits, size_t num_classes, 
                              float temperature, float safety_threshold,
                              ts_decision_t* out_decision) {
    if (!logits || !out_decision || num_classes == 0 || num_classes > TS_MAX_CLASSES) {
        return TS_ERR_INVALID_PARAM;
    }

    float stack_probs[TS_MAX_CLASSES];
    ts_status_t status = ts_calibrate_logits(logits, num_classes, temperature, stack_probs);
    if (status != TS_SUCCESS) {
        return status;
    }

    size_t best_idx = 0;
    float max_conf = stack_probs[0];
    for (size_t i = 1; i < num_classes; ++i) {
        if (stack_probs[i] > max_conf) {
            max_conf = stack_probs[i];
            best_idx = i;
        }
    }

    out_decision->predicted_class = best_idx;
    out_decision->calibrated_confidence = max_conf;
    out_decision->is_safe_to_execute = (max_conf >= safety_threshold);

    return TS_SUCCESS;
}

ts_status_t ts_compute_metrics(const ts_dataset_t* dataset, float temperature,
                              size_t num_bins, ts_metrics_t* out_metrics) {
    if (!dataset || !out_metrics || dataset->num_samples == 0 || 
        dataset->num_classes == 0 || num_bins == 0 || num_bins > TS_MAX_BINS || temperature <= 0.0f) {
        return TS_ERR_INVALID_PARAM;
    }

    size_t bin_counts[TS_MAX_BINS] = {0};
    double bin_conf_sum[TS_MAX_BINS] = {0.0};
    size_t bin_correct_counts[TS_MAX_BINS] = {0};

    const float bin_width = 1.0f / (float)num_bins;
    double total_nll = 0.0;
    double total_brier = 0.0;
    float prob_buf[TS_MAX_CLASSES];

    for (size_t i = 0; i < dataset->num_samples; ++i) {
        const float* sample_logits = dataset->logits_flat + (i * dataset->num_classes);
        size_t true_label = dataset->labels[i];

        ts_status_t status = ts_calibrate_logits(sample_logits, dataset->num_classes, temperature, prob_buf);
        if (status != TS_SUCCESS) return status;

        size_t pred_class = 0;
        float max_prob = prob_buf[0];
        for (size_t c = 1; c < dataset->num_classes; ++c) {
            if (prob_buf[c] > max_prob) {
                max_prob = prob_buf[c];
                pred_class = c;
            }
        }

        bool is_correct = (pred_class == true_label);
        float conf = max_prob;
        if (conf < 0.0f) conf = 0.0f;
        if (conf > 1.0f) conf = 1.0f;

        size_t b_idx = (size_t)(conf / bin_width);
        if (b_idx >= num_bins) b_idx = num_bins - 1;

        bin_counts[b_idx]++;
        bin_conf_sum[b_idx] += (double)conf;
        if (is_correct) bin_correct_counts[b_idx]++;

        /* Накопичення NLL */
        if (true_label < dataset->num_classes) {
            float p_true = prob_buf[true_label];
            if (p_true < 1e-12f) p_true = 1e-12f;
            total_nll -= log((double)p_true);
        }

        /* Накопичення балу Браєра */
        for (size_t c = 0; c < dataset->num_classes; ++c) {
            double target = (c == true_label) ? 1.0 : 0.0;
            double diff = (double)prob_buf[c] - target;
            total_brier += diff * diff;
        }
    }

    const double n_samples = (double)dataset->num_samples;
    double total_ece = 0.0;
    double max_mce = 0.0;

    for (size_t b = 0; b < num_bins; ++b) {
        if (bin_counts[b] > 0) {
            double avg_conf = bin_conf_sum[b] / (double)bin_counts[b];
            double avg_acc = (double)bin_correct_counts[b] / (double)bin_counts[b];
            double gap = fabs(avg_acc - avg_conf);
            double weight = (double)bin_counts[b] / n_samples;
            total_ece += weight * gap;
            if (gap > max_mce) max_mce = gap;
        }
    }

    out_metrics->ece = (float)total_ece;
    out_metrics->mce = (float)max_mce;
    out_metrics->brier_score = (float)(total_brier / n_samples);
    out_metrics->nll = (float)(total_nll / n_samples);

    return TS_SUCCESS;
}

static double ts_eval_dataset_nll_beta(const ts_dataset_t* dataset, double beta) {
    double total_nll = 0.0;
    for (size_t i = 0; i < dataset->num_samples; ++i) {
        const float* z = dataset->logits_flat + (i * dataset->num_classes);
        size_t y = dataset->labels[i];

        double max_z = (double)z[0] * beta;
        for (size_t c = 1; c < dataset->num_classes; ++c) {
            double val = (double)z[c] * beta;
            if (val > max_z) max_z = val;
        }

        double sum_exp = 0.0;
        for (size_t c = 0; c < dataset->num_classes; ++c) {
            sum_exp += exp((double)z[c] * beta - max_z);
        }

        if (y < dataset->num_classes) {
            double log_p_true = ((double)z[y] * beta - max_z) - log(sum_exp);
            total_nll -= log_p_true;
        }
    }
    return total_nll / (double)dataset->num_samples;
}

ts_status_t ts_optimize_temperature(const ts_dataset_t* dataset, 
                                   float min_temp, float max_temp,
                                   size_t max_iterations, float tolerance,
                                   float* out_optimal_temperature) {
    if (!dataset || !out_optimal_temperature || dataset->num_samples == 0 ||
        min_temp <= 0.0f || max_temp <= min_temp) {
        return TS_ERR_INVALID_PARAM;
    }

    double beta_min = 1.0 / (double)max_temp;
    double beta_max = 1.0 / (double)min_temp;

    const double phi_res = 0.38196601125010515; // 2 - φ

    double a = beta_min;
    double b = beta_max;
    double c = a + phi_res * (b - a);
    double d = b - phi_res * (b - a);
    double fc = ts_eval_dataset_nll_beta(dataset, c);
    double fd = ts_eval_dataset_nll_beta(dataset, d);

    for (size_t iter = 0; iter < max_iterations; ++iter) {
        if (fabs(b - a) < (double)tolerance) {
            break;
        }

        if (fc < fd) {
            b = d;
            d = c;
            fd = fc;
            c = a + phi_res * (b - a);
            fc = ts_eval_dataset_nll_beta(dataset, c);
        } else {
            a = c;
            c = d;
            fc = fd;
            d = b - phi_res * (b - a);
            fd = ts_eval_dataset_nll_beta(dataset, d);
        }
    }

    double best_beta = (a + b) * 0.5;
    if (best_beta <= 0.0) {
        return TS_ERR_OPTIMIZATION_FAILED;
    }

    *out_optimal_temperature = (float)(1.0 / best_beta);
    return TS_SUCCESS;
}
