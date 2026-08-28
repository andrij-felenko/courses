#include <math.h>
#include <stddef.h>
#include <stdbool.h>
#include <float.h>

#define MAX_CALIBRATION_BINS 64

/* Структура результату порогового контролю безпеки */
typedef struct {
    size_t predicted_class;
    float calibrated_confidence;
    bool is_safe_to_execute;
} DecisionResult;

/* Чисельно стабільний температурний Softmax */
bool calibrate_softmax_c(const float* logits, size_t num_classes, float temperature, float* out_probs) {
    if (!logits || !out_probs || num_classes == 0 || temperature <= 0.0f) {
        return false;
    }

    const float inv_t = 1.0f / temperature;

    /* Знаходимо максимальний масштабований логіт для запобігання переповненню exp */
    float max_scaled_logit = logits[0] * inv_t;
    for (size_t i = 1; i < num_classes; ++i) {
        float scaled = logits[i] * inv_t;
        if (scaled > max_scaled_logit) {
            max_scaled_logit = scaled;
        }
    }

    /* Обчислюємо експоненти та накопичуємо суму */
    float sum_exp = 0.0f;
    for (size_t i = 0; i < num_classes; ++i) {
        float exp_val = expf(logits[i] * inv_t - max_scaled_logit);
        out_probs[i] = exp_val;
        sum_exp += exp_val;
    }

    if (sum_exp <= 0.0f || isnan(sum_exp)) {
        return false;
    }

    /* Нормалізація розподілу до одиничної суми */
    const float inv_sum = 1.0f / sum_exp;
    for (size_t i = 0; i < num_classes; ++i) {
        out_probs[i] *= inv_sum;
    }

    return true;
}

/* Прийняття рішення з пороговою перевіркою безпеки */
DecisionResult evaluate_decision_safety_c(const float* logits, size_t num_classes, 
                                         float temperature, float safety_threshold) {
    DecisionResult result = {0, 0.0f, false};
    if (!logits || num_classes == 0) return result;

    #define STACK_PROBS_MAX 128
    float probs_buf[STACK_PROBS_MAX];
    float* probs = probs_buf;
    if (num_classes > STACK_PROBS_MAX) return result;

    if (!calibrate_softmax_c(logits, num_classes, temperature, probs)) {
        return result;
    }

    size_t best_idx = 0;
    float max_conf = probs[0];
    for (size_t i = 1; i < num_classes; ++i) {
        if (probs[i] > max_conf) {
            max_conf = probs[i];
            best_idx = i;
        }
    }

    result.predicted_class = best_idx;
    result.calibrated_confidence = max_conf;
    result.is_safe_to_execute = (max_conf >= safety_threshold);

    return result;
}

/* Розрахунок ECE (Expected Calibration Error) за рівномірними бінами */
float compute_ece_c(const float* confidences, const bool* correct_flags, size_t num_samples, size_t num_bins) {
    if (!confidences || !correct_flags || num_samples == 0 || num_bins == 0) {
        return 0.0f;
    }

    if (num_bins > MAX_CALIBRATION_BINS) {
        num_bins = MAX_CALIBRATION_BINS;
    }

    size_t bin_counts[MAX_CALIBRATION_BINS] = {0};
    float bin_conf_sum[MAX_CALIBRATION_BINS] = {0.0f};
    size_t bin_correct_sum[MAX_CALIBRATION_BINS] = {0};

    const float bin_width = 1.0f / (float)num_bins;

    /* Розподіл передбачень по бінах */
    for (size_t i = 0; i < num_samples; ++i) {
        float conf = confidences[i];
        if (conf < 0.0f) conf = 0.0f;
        if (conf > 1.0f) conf = 1.0f;

        size_t bin_idx = (size_t)(conf / bin_width);
        if (bin_idx >= num_bins) {
            bin_idx = num_bins - 1;
        }

        bin_counts[bin_idx]++;
        bin_conf_sum[bin_idx] += conf;
        if (correct_flags[i]) {
            bin_correct_sum[bin_idx]++;
        }
    }

    /* Зважена сума похибок калібрування */
    float total_ece = 0.0f;
    for (size_t b = 0; b < num_bins; ++b) {
        if (bin_counts[b] > 0) {
            float avg_conf = bin_conf_sum[b] / (float)bin_counts[b];
            float avg_acc = (float)bin_correct_sum[b] / (float)bin_counts[b];
            float weight = (float)bin_counts[b] / (float)num_samples;
            total_ece += weight * fabsf(avg_acc - avg_conf);
        }
    }

    return total_ece;
}
