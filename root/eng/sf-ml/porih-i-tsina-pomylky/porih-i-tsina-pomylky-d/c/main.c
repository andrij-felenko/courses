#include <stdbool.h>
#include <stdint.h>
#include <math.h>

/* Матриця вартостей помилок та рішень */
typedef struct {
    float cost_tp;  /* Вартість True Positive */
    float cost_fp;  /* Вартість False Positive */
    float cost_tn;  /* Вартість True Negative */
    float cost_fn;  /* Вартість False Negative */
} cost_matrix_t;

/* Стан оптимізатора порогу */
typedef struct {
    cost_matrix_t costs;
    float prior_positive;  /* P(Y = 1) */
    float prior_negative;  /* P(Y = 0) */
    float optimal_threshold;
} threshold_engine_t;

/* Обчислення оптимального байєсівського порогу T* */
bool threshold_engine_init(threshold_engine_t *eng, cost_matrix_t costs, float prior_pos) {
    if (!eng || prior_pos <= 0.0f || prior_pos >= 1.0f) {
        return false;
    }
    
    eng->costs = costs;
    eng->prior_positive = prior_pos;
    eng->prior_negative = 1.0f - prior_pos;
    
    float num = costs.cost_fp - costs.cost_tn;
    float den = (costs.cost_fp - costs.cost_tn) + (costs.cost_fn - costs.cost_tp);
    
    if (den <= 0.0f || num < 0.0f) {
        /* Некоректні вартості: помилка дешевша за правильне рішення */
        return false;
    }
    
    /* Поріг для каліброваної апостеріорної ймовірності P(Y=1|x) */
    eng->optimal_threshold = num / den;
    return true;
}

/* Класифікація вихідної ймовірності з урахуванням порогу */
typedef struct {
    bool decision;        /* true = Positive (1), false = Negative (0) */
    float expected_loss;  /* Очікувані втрати за ухваленого рішення */
    float confidence_margin;
} classification_result_t;

classification_result_t threshold_classify(const threshold_engine_t *eng, float prob_pos) {
    classification_result_t res;
    if (prob_pos < 0.0f) prob_pos = 0.0f;
    if (prob_pos > 1.0f) prob_pos = 1.0f;
    
    float prob_neg = 1.0f - prob_pos;
    
    /* Розрахунок очікуваних втрат для обох гілок */
    float risk_action = prob_pos * eng->costs.cost_tp + prob_neg * eng->costs.cost_fp;
    float risk_inaction = prob_pos * eng->costs.cost_fn + prob_neg * eng->costs.cost_tn;
    
    if (prob_pos >= eng->optimal_threshold) {
        res.decision = true;
        res.expected_loss = risk_action;
    } else {
        res.decision = false;
        res.expected_loss = risk_inaction;
    }
    
    res.confidence_margin = fabsf(prob_pos - eng->optimal_threshold);
    return res;
}
