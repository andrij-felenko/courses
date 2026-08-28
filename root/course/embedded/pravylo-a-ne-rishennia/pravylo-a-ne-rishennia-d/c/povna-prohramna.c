#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MAX_FACTS           16
#define MAX_RULES           8
#define MAX_INTERLOCK_BITS  32

/* Ідентифікатори фактів у системі */
typedef enum {
    FACT_VOLTAGE_MV = 0,
    FACT_CURRENT_MA,
    FACT_TEMP_C,
    FACT_PRESSURE_KPA,
    FACT_ESTOP_PRESSED,
    FACT_COUNT
} fact_id_t;

/* Оператори порівняння умов */
typedef enum {
    OP_LESS_THAN = 0,
    OP_GREATER_THAN,
    OP_EQUALS,
    OP_IN_RANGE,
    OP_BIT_SET
} condition_op_t;

/* Структура збереження факту */
typedef struct {
    int32_t value;
    uint32_t last_update_ms;
    bool is_valid;
} fact_t;

/* Дія, яку викликає правило */
typedef void (*action_fn_t)(void *context, int32_t param);

/* Опис статичного правила (розміщується у Flash/ROM) */
typedef struct {
    uint8_t rule_id;
    fact_id_t fact_id;
    condition_op_t op;
    int32_t threshold_low;
    int32_t threshold_high;
    uint32_t dwell_time_ms;     /* Необхідна тривалість істинності умови */
    uint32_t interlock_mask;    /* Біти несумісних станів, що блокують правило */
    uint32_t set_interlock;     /* Біти блокувань, які активує це правило */
    action_fn_t action;
    int32_t action_param;
} rule_def_t;

/* Динамічний стан правила у RAM */
typedef struct {
    uint32_t condition_true_since_ms;
    bool is_active;
    bool condition_was_true;
} rule_state_t;

/* Стан усього рушія правил */
typedef struct {
    fact_t facts[MAX_FACTS];
    rule_state_t rule_states[MAX_RULES];
    const rule_def_t *rules;
    size_t rule_count;
    uint32_t active_interlocks;
    void *user_context;
} rule_engine_t;

/* Ініціалізація рушія */
void rule_engine_init(rule_engine_t *engine, const rule_def_t *rules, 
                      size_t rule_count, void *context) {
    if (!engine || !rules || rule_count > MAX_RULES) {
        return;
    }
    engine->rules = rules;
    engine->rule_count = rule_count;
    engine->user_context = context;
    engine->active_interlocks = 0;

    for (size_t i = 0; i < MAX_FACTS; ++i) {
        engine->facts[i].value = 0;
        engine->facts[i].last_update_ms = 0;
        engine->facts[i].is_valid = false;
    }
    for (size_t i = 0; i < MAX_RULES; ++i) {
        engine->rule_states[i].condition_true_since_ms = 0;
        engine->rule_states[i].is_active = false;
        engine->rule_states[i].condition_was_true = false;
    }
}

/* Оновлення факту від сенсора або зовнішньої підсистеми */
void rule_engine_set_fact(rule_engine_t *engine, fact_id_t id, 
                          int32_t val, uint32_t now_ms) {
    if (!engine || id >= MAX_FACTS) {
        return;
    }
    engine->facts[id].value = val;
    engine->facts[id].last_update_ms = now_ms;
    engine->facts[id].is_valid = true;
}

/* Позначення факту як невалідного (обрив сенсора, тайм-аут) */
void rule_engine_invalidate_fact(rule_engine_t *engine, fact_id_t id) {
    if (!engine || id >= MAX_FACTS) {
        return;
    }
    engine->facts[id].is_valid = false;
}

/* Обчислення істинності окремого предиката */
static bool evaluate_condition(const rule_def_t *rule, const fact_t *fact) {
    if (!fact->is_valid) {
        return false;
    }
    switch (rule->op) {
        case OP_LESS_THAN:
            return fact->value < rule->threshold_low;
        case OP_GREATER_THAN:
            return fact->value > rule->threshold_high;
        case OP_EQUALS:
            return fact->value == rule->threshold_low;
        case OP_IN_RANGE:
            return (fact->value >= rule->threshold_low) && 
                   (fact->value <= rule->threshold_high);
        case OP_BIT_SET:
            return (fact->value & rule->threshold_low) != 0;
        default:
            return false;
    }
}

/* Основний крок обробки правил у циклі реального часу */
void rule_engine_step(rule_engine_t *engine, uint32_t now_ms) {
    if (!engine || !engine->rules) {
        return;
    }

    /* Очищення динамічних блокувань перед новим проходом */
    uint32_t next_interlocks = 0;

    for (size_t i = 0; i < engine->rule_count; ++i) {
        const rule_def_t *r = &engine->rules[i];
        rule_state_t *st = &engine->rule_states[i];
        const fact_t *f = &engine->facts[r->fact_id];

        /* Перевірка апаратних та системних блокувань */
        if ((engine->active_interlocks & r->interlock_mask) != 0) {
            st->condition_was_true = false;
            st->is_active = false;
            continue;
        }

        bool cond = evaluate_condition(r, f);

        if (cond) {
            if (!st->condition_was_true) {
                st->condition_was_true = true;
                st->condition_true_since_ms = now_ms;
            }

            /* Перевірка витримки часу (dwell time / debounce) */
            if ((now_ms - st->condition_true_since_ms) >= r->dwell_time_ms) {
                if (!st->is_active) {
                    st->is_active = true;
                    if (r->action) {
                        r->action(engine->user_context, r->action_param);
                    }
                }
                next_interlocks |= r->set_interlock;
            }
        } else {
            st->condition_was_true = false;
            st->is_active = false;
        }
    }

    engine->active_interlocks = next_interlocks;
}
