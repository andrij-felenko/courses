#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define MAX_CLASSES 8

typedef enum {
    DECISION_ACCEPTED = 0,
    DECISION_REJECT_OOD = 1,
    DECISION_REJECT_AMBIGUOUS = 2
} decision_status_t;

typedef struct {
    int class_id;
    float confidence;
    float energy;
    float normalized_entropy;
    decision_status_t status;
} selective_result_t;

selective_result_t classify_selective(
    const float* logits,
    int num_classes,
    float temperature,
    float energy_threshold,
    float entropy_threshold
) {
    selective_result_t res = {
        .class_id = -1,
        .confidence = 0.0f,
        .energy = 0.0f,
        .normalized_entropy = 0.0f,
        .status = DECISION_ACCEPTED
    };

    if (num_classes <= 0 || num_classes > MAX_CLASSES || temperature <= 0.0f) {
        res.status = DECISION_REJECT_OOD;
        return res;
    }

    // 1. Пошук максимального логіта для чисельної стабільності LogSumExp
    float max_logit = logits[0];
    int argmax_idx = 0;
    for (int i = 1; i < num_classes; ++i) {
        if (logits[i] > max_logit) {
            max_logit = logits[i];
            argmax_idx = i;
        }
    }

    // 2. Обчислення вільної енергії: E(x) = -T * (max/T + ln(sum(e^{(f_i - max)/T})))
    float sum_exp = 0.0f;
    float exp_scaled[MAX_CLASSES];
    for (int i = 0; i < num_classes; ++i) {
        exp_scaled[i] = expf((logits[i] - max_logit) / temperature);
        sum_exp += exp_scaled[i];
    }
    res.energy = -temperature * ((max_logit / temperature) + logf(sum_exp));

    // Перевірка OOD-гейта за вільною енергією (чим більша енергія, тим далі від ID)
    if (res.energy > energy_threshold) {
        res.status = DECISION_REJECT_OOD;
        return res;
    }

    // 3. Обчислення ймовірностей Softmax та ентропії Шеннона
    float probs[MAX_CLASSES];
    float entropy = 0.0f;
    for (int i = 0; i < num_classes; ++i) {
        probs[i] = exp_scaled[i] / sum_exp;
        if (probs[i] > 1e-8f) {
            entropy -= probs[i] * logf(probs[i]);
        }
    }

    float max_entropy = logf((float)num_classes);
    res.normalized_entropy = (max_entropy > 0.0f) ? (entropy / max_entropy) : 0.0f;
    res.confidence = probs[argmax_idx];
    res.class_id = argmax_idx;

    // Перевірка гейта алеаторної неоднозначності за ентропією
    if (res.normalized_entropy > entropy_threshold) {
        res.status = DECISION_REJECT_AMBIGUOUS;
        return res;
    }

    res.status = DECISION_ACCEPTED;
    return res;
}
