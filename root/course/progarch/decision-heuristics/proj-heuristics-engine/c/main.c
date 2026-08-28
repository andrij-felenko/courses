#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

// Ідіоматичний C11: чіткі межі пам'яті, явні коди помилок, відсутність динамічного виділення

typedef enum {
    DECISION_ROUTE_FAST_TRACK = 0,
    DECISION_ROUTE_TIMEBOXED_SPIKE,
    DECISION_ROUTE_PRE_MORTEM,
    DECISION_ROUTE_ARCH_REVIEW,
    DECISION_ROUTE_REJECTED_NO_METRICS
} decision_route_t;

typedef enum {
    EVAL_OK = 0,
    EVAL_ERR_TOKEN_BUDGET_EXCEEDED,
    EVAL_ERR_INVALID_REVERSIBILITY,
    EVAL_ERR_INVALID_RISK
} eval_error_t;

typedef struct {
    const char* title;
    float reversibility_score;       // 0.0 .. 1.0
    uint8_t innovation_tokens;       // 0 .. 3
    bool has_measurement_data;
    uint8_t risk_severity;           // 1 .. 5
    bool touches_public_api;
    bool is_performance_optimization;
} decision_vector_t;

typedef struct {
    decision_route_t route;
    float one_way_index;
    const char* rationale;
} evaluation_result_t;

eval_error_t evaluate_decision(const decision_vector_t* vec, 
                                uint8_t current_project_tokens, 
                                evaluation_result_t* out_result) {
    if (!vec || !out_result) return EVAL_ERR_INVALID_REVERSIBILITY;

    if (vec->reversibility_score < 0.0f || vec->reversibility_score > 1.0f) {
        return EVAL_ERR_INVALID_REVERSIBILITY;
    }
    if (vec->risk_severity < 1 || vec->risk_severity > 5) {
        return EVAL_ERR_INVALID_RISK;
    }
    if (current_project_tokens + vec->innovation_tokens > 3) {
        return EVAL_ERR_TOKEN_BUDGET_EXCEEDED;
    }

    // Евристика: Measure First
    if (vec->is_performance_optimization && !vec->has_measurement_data) {
        out_result->route = DECISION_ROUTE_REJECTED_NO_METRICS;
        out_result->one_way_index = 0.0f;
        out_result->rationale = "Відхилено: оптимізація продуктивності заборонена без метрик";
        return EVAL_OK;
    }

    float public_impact = vec->touches_public_api ? 0.3f : 0.0f;
    float token_impact = (float)vec->innovation_tokens * 0.1f;
    float one_way_index = (1.0f - vec->reversibility_score) * 0.5f + public_impact + token_impact;

    out_result->one_way_index = one_way_index;

    if (one_way_index >= 0.6f || vec->risk_severity >= 4) {
        out_result->route = DECISION_ROUTE_ARCH_REVIEW;
        out_result->rationale = "One-Way Door: Високий ризик. Потрібен Arch Review Board.";
    } else if (vec->risk_severity == 3 || (one_way_index >= 0.3f && !vec->has_measurement_data)) {
        out_result->route = DECISION_ROUTE_PRE_MORTEM;
        out_result->rationale = "Помірний ризик. Обов'язкова сесія Pre-Mortem.";
    } else if (vec->reversibility_score < 0.7f || vec->innovation_tokens > 0) {
        out_result->route = DECISION_ROUTE_TIMEBOXED_SPIKE;
        out_result->rationale = "Купити інформацію: Timeboxed спайк на 2 дні.";
    } else {
        out_result->route = DECISION_ROUTE_FAST_TRACK;
        out_result->rationale = "Two-Way Door: Висока зворотність. Делегувати розробнику.";
    }

    return EVAL_OK;
}

int main(void) {
    decision_vector_t prop = {
        .title = "Рефакторинг внутрішнього сервісу авторизації",
        .reversibility_score = 0.85f,
        .innovation_tokens = 0,
        .has_measurement_data = true,
        .risk_severity = 2,
        .touches_public_api = false,
        .is_performance_optimization = false
    };

    evaluation_result_t res;
    eval_error_t err = evaluate_decision(&prop, 1, &res);

    if (err == EVAL_OK) {
        printf("Маршрут рішення: %s (Індекс: %.2f)\n", res.rationale, res.one_way_index);
    } else {
        printf("Помилка оцінки: %d\n", err);
    }

    return 0;
}
