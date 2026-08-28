#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <float.h>

#define SELECTIVE_MAX_CLASSES 16
#define SELECTIVE_EPSILON     1e-8f

typedef enum {
    SELECTIVE_OK = 0,
    SELECTIVE_ERR_INVALID_ARG = -1
} selective_error_t;

typedef enum {
    DECISION_STATUS_ACCEPTED = 0,
    DECISION_STATUS_REJECT_OOD = 1,
    DECISION_STATUS_REJECT_AMBIGUOUS = 2
} decision_status_t;

typedef struct {
    float temperature;        // Температура масштабування (типово 1.0f)
    float energy_threshold;   // Верхній поріг вільної енергії (наприклад, -5.0f)
    float entropy_threshold;  // Верхній поріг нормованої ентропії [0.0..1.0] (типово 0.40f)
} selective_config_t;

typedef struct {
    int predicted_class;      // Індекс класу з максимальним логітом
    float confidence;         // Ймовірність обраного класу [0.0..1.0]
    float free_energy;        // Обчислена вільна енергія Гельмгольца
    float normalized_entropy; // Нормована ентропія Шеннона [0.0..1.0]
    decision_status_t status; // Результат фільтрації (дозвіл чи тип відмови)
} selective_output_t;

selective_error_t selective_classify_process(
    const selective_config_t* config,
    const float* logits,
    size_t num_classes,
    selective_output_t* out_result
) {
    if (!config || !logits || !out_result) {
        return SELECTIVE_ERR_INVALID_ARG;
    }
    if (num_classes < 2 || num_classes > SELECTIVE_MAX_CLASSES) {
        return SELECTIVE_ERR_INVALID_ARG;
    }
    if (config->temperature <= SELECTIVE_EPSILON) {
        return SELECTIVE_ERR_INVALID_ARG;
    }
    if (config->entropy_threshold < 0.0f || config->entropy_threshold > 1.0f) {
        return SELECTIVE_ERR_INVALID_ARG;
    }

    out_result->predicted_class = -1;
    out_result->confidence = 0.0f;
    out_result->free_energy = 0.0f;
    out_result->normalized_entropy = 1.0f;
    out_result->status = DECISION_STATUS_REJECT_OOD;

    // 1. Знаходження максимального логіта для безпечного LogSumExp
    float max_logit = logits[0];
    size_t argmax_idx = 0;
    for (size_t i = 1; i < num_classes; ++i) {
        if (logits[i] > max_logit) {
            max_logit = logits[i];
            argmax_idx = i;
        }
    }
    out_result->predicted_class = (int)argmax_idx;

    // 2. Обчислення зсунутих експонент та їх суми
    float exp_scaled[SELECTIVE_MAX_CLASSES];
    float sum_exp = 0.0f;
    const float inv_temp = 1.0f / config->temperature;

    for (size_t i = 0; i < num_classes; ++i) {
        float scaled_diff = (logits[i] - max_logit) * inv_temp;
        exp_scaled[i] = expf(scaled_diff);
        sum_exp += exp_scaled[i];
    }

    if (sum_exp <= SELECTIVE_EPSILON) {
        out_result->status = DECISION_STATUS_REJECT_OOD;
        return SELECTIVE_OK;
    }

    // 3. Обчислення вільної енергії Гельмгольца: E(x) = -T * (max/T + ln(sum))
    out_result->free_energy = -max_logit - (config->temperature * logf(sum_exp));

    // Гейт 1: Перевірка на сторонні дані поза розподілом (OOD)
    if (out_result->free_energy > config->energy_threshold) {
        out_result->status = DECISION_STATUS_REJECT_OOD;
        return SELECTIVE_OK;
    }

    // 4. Розрахунок Softmax-ймовірностей та ентропії Шеннона
    float entropy = 0.0f;
    const float inv_sum_exp = 1.0f / sum_exp;

    for (size_t i = 0; i < num_classes; ++i) {
        float p = exp_scaled[i] * inv_sum_exp;
        if (p > SELECTIVE_EPSILON) {
            entropy -= p * logf(p);
        }
    }

    const float max_entropy = logf((float)num_classes);
    out_result->normalized_entropy = (max_entropy > SELECTIVE_EPSILON) ? (entropy / max_entropy) : 0.0f;
    out_result->confidence = exp_scaled[argmax_idx] * inv_sum_exp;

    // Гейт 2: Перевірка на алеаторну неоднозначність (шум/межа класів)
    if (out_result->normalized_entropy > config->entropy_threshold) {
        out_result->status = DECISION_STATUS_REJECT_AMBIGUOUS;
        return SELECTIVE_OK;
    }

    out_result->status = DECISION_STATUS_ACCEPTED;
    return SELECTIVE_OK;
}

// ── Модульні тести ────────────────────────────────────────────────────────
static void run_test(const char* name, const float* logits, size_t n, const selective_config_t* cfg, decision_status_t expected_status) {
    selective_output_t res;
    selective_error_t err = selective_classify_process(cfg, logits, n, &res);
    
    printf("[%s] Тест: %s\n", (err == SELECTIVE_OK && res.status == expected_status) ? "PASS" : "FAIL", name);
    printf("  -> Статус: %d (очікувався: %d), Клас: %d, Впевненість: %.4f, Енергія: %.3f, Ентропія: %.3f\n",
           res.status, expected_status, res.predicted_class, res.confidence, res.free_energy, res.normalized_entropy);
}

int main(void) {
    selective_config_t cfg = {
        .temperature = 1.0f,
        .energy_threshold = -5.0f,
        .entropy_threshold = 0.40f
    };

    printf("=== Запуск тестів вибіркового класифікатора (C99) ===\n");

    // 1. Чіткий In-Distribution вхід (Клас 0 домінує)
    float id_logits[4] = { 8.5f, 1.2f, 0.4f, -0.8f };
    run_test("In-Distribution (чітке розпізнавання)", id_logits, 4, &cfg, DECISION_STATUS_ACCEPTED);

    // 2. Алеаторний зашумлений вхід (Клас 1 і Клас 2 рівнозначні)
    float noisy_logits[4] = { 0.2f, 5.0f, 4.9f, 0.1f };
    run_test("Ambiguous Noise (висока ентропія на межі)", noisy_logits, 4, &cfg, DECISION_STATUS_REJECT_AMBIGUOUS);

    // 3. Слабкий фоновий OOD шум (всі логіти близькі до нуля)
    float ood_low_logits[4] = { 0.1f, -0.2f, 0.05f, -0.1f };
    run_test("OOD Background Noise (висока вільна енергія)", ood_low_logits, 4, &cfg, DECISION_STATUS_REJECT_OOD);

    // 4. Патологічний OOD із штучно зміщеним логітом (Softmax Overconfidence)
    float ood_overconf_logits[4] = { 2.1f, -1.0f, -0.5f, -2.0f };
    run_test("OOD Weak Confidence", ood_overconf_logits, 4, &cfg, DECISION_STATUS_REJECT_OOD);

    return 0;
}
