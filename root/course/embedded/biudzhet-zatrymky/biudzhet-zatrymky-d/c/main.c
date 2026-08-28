#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_STAGES 16

typedef enum {
    STAGE_DETERMINISTIC,  // Стала затримка (наприклад, DShot передача)
    STAGE_QUANTIZATION,   // Квантування періоду (0.5 * T_period)
    STAGE_STOCHASTIC      // Ймовірнісна затримка з джитером
} stage_type_t;

typedef struct {
    const char *name;
    stage_type_t type;
    float min_ms;
    float typ_ms;
    float max_ms;
} latency_stage_t;

typedef struct {
    latency_stage_t stages[MAX_STAGES];
    uint8_t count;
} latency_pipeline_t;

typedef struct {
    float total_min_ms;
    float total_typ_ms;
    float total_max_ms;
    float jitter_ms;
} pipeline_budget_t;

void pipeline_init(latency_pipeline_t *pipe) {
    pipe->count = 0;
}

bool pipeline_add_stage(latency_pipeline_t *pipe, const char *name, 
                        stage_type_t type, float min_ms, float typ_ms, float max_ms) {
    if (pipe->count >= MAX_STAGES) return false;
    latency_stage_t *st = &pipe->stages[pipe->count++];
    st->name = name;
    st->type = type;
    st->min_ms = min_ms;
    st->typ_ms = typ_ms;
    st->max_ms = max_ms;
    return true;
}

pipeline_budget_t pipeline_calculate(const latency_pipeline_t *pipe) {
    pipeline_budget_t budget = {0.0f, 0.0f, 0.0f, 0.0f};
    for (uint8_t i = 0; i < pipe->count; i++) {
        const latency_stage_t *st = &pipe->stages[i];
        budget.total_min_ms += st->min_ms;
        budget.total_typ_ms += st->typ_ms;
        budget.total_max_ms += st->max_ms;
    }
    budget.jitter_ms = budget.total_max_ms - budget.total_min_ms;
    return budget;
}

void pipeline_print_report(const latency_pipeline_t *pipe, const char *title) {
    pipeline_budget_t b = pipeline_calculate(pipe);
    printf("====================================================\n");
    printf(" БЮДЖЕТ ЗАРИМКИ: %s\n", title);
    printf("----------------------------------------------------\n");
    printf(" %-22s | %-8s | %-8s | %-8s\n", "Ланка тракту", "Min(мс)", "Typ(мс)", "Max(мс)");
    printf("----------------------------------------------------\n");
    for (uint8_t i = 0; i < pipe->count; i++) {
        const latency_stage_t *st = &pipe->stages[i];
        printf(" %-22s | %8.2f | %8.2f | %8.2f\n", 
               st->name, st->min_ms, st->typ_ms, st->max_ms);
    }
    printf("----------------------------------------------------\n");
    printf(" РАЗОМ:                  | %8.2f | %8.2f | %8.2f\n", 
           b.total_min_ms, b.total_typ_ms, b.total_max_ms);
    printf(" ДЖИТЕР ТРАКТУ:          | %8.2f мс\n", b.jitter_ms);
    printf("====================================================\n\n");
}
