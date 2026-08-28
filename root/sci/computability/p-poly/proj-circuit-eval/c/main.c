#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Типи логічних елементів схеми */
typedef enum {
    GATE_INPUT_X,  /* Звичайний вхідний біт рядка x */
    GATE_ADVICE_A, /* Біт підказки a_n */
    GATE_NOT,      /* Інвертор */
    GATE_AND,      /* Кон'юнкт */
    GATE_OR        /* Диз'юнкт */
} GateType;

/* Вузол булевої схеми (DAG) */
typedef struct {
    GateType type;
    size_t param_idx; /* Індекс у масиві x або a_n для входів */
    size_t in1;       /* Індекс першого вхідного гейта */
    size_t in2;       /* Індекс другого вхідного гейта */
} Gate;

/* Структура булевої схеми P/poly */
typedef struct {
    size_t num_inputs;
    size_t num_advice;
    size_t num_gates;
    Gate *gates;
} Circuit;

/* Ініціалізація схеми */
Circuit* circuit_create(size_t num_inputs, size_t num_advice, size_t num_gates) {
    Circuit *c = (Circuit*)malloc(sizeof(Circuit));
    if (!c) return NULL;
    c->num_inputs = num_inputs;
    c->num_advice = num_advice;
    c->num_gates = num_gates;
    c->gates = (Gate*)calloc(num_gates, sizeof(Gate));
    if (!c->gates) {
        free(c);
        return NULL;
    }
    return c;
}

/* Звільнення ресурсів схеми */
void circuit_free(Circuit *c) {
    if (c) {
        free(c->gates);
        free(c);
    }
}

/* Оцінка схеми C_n на вході x та підказці a_n */
bool circuit_eval(const Circuit *c, const uint8_t *x, const uint8_t *a_n) {
    if (!c || !x || !a_n || c->num_gates == 0) return false;

    uint8_t *values = (uint8_t*)calloc(c->num_gates, sizeof(uint8_t));
    if (!values) return false;

    for (size_t i = 0; i < c->num_gates; ++i) {
        const Gate *g = &c->gates[i];
        switch (g->type) {
            case GATE_INPUT_X:
                values[i] = (g->param_idx < c->num_inputs) ? x[g->param_idx] : 0;
                break;
            case GATE_ADVICE_A:
                values[i] = (g->param_idx < c->num_advice) ? a_n[g->param_idx] : 0;
                break;
            case GATE_NOT:
                values[i] = !values[g->in1];
                break;
            case GATE_AND:
                values[i] = values[g->in1] && values[g->in2];
                break;
            case GATE_OR:
                values[i] = values[g->in1] || values[g->in2];
                break;
        }
    }

    /* Останній гейт вважається виходом схеми */
    bool result = (values[c->num_gates - 1] != 0);
    free(values);
    return result;
}

int main(void) {
    /* Побудова демонстраційної схеми: C(x1, x2; a1) = (x1 AND x2) OR (x1 AND NOT a1) */
    size_t num_inputs = 2;
    size_t num_advice = 1;
    size_t num_gates = 6;

    Circuit *c = circuit_create(num_inputs, num_advice, num_gates);
    if (!c) return 1;

    /* Гейти 0, 1: входи x1, x2 */
    c->gates[0] = (Gate){ GATE_INPUT_X, 0, 0, 0 };
    c->gates[1] = (Gate){ GATE_INPUT_X, 1, 0, 0 };
    /* Гейт 2: підказка a1 */
    c->gates[2] = (Gate){ GATE_ADVICE_A, 0, 0, 0 };
    /* Гейт 3: NOT a1 */
    c->gates[3] = (Gate){ GATE_NOT, 0, 2, 0 };
    /* Гейт 4: x1 AND x2 */
    c->gates[4] = (Gate){ GATE_AND, 0, 0, 1 };
    /* Гейт 5 (вихід): (x1 AND x2) OR (NOT a1) */
    c->gates[5] = (Gate){ GATE_OR, 0, 4, 3 };

    uint8_t x[2] = {1, 0};
    uint8_t a_n[1] = {0}; /* Підказка: a1 = 0 */

    bool res = circuit_eval(c, x, a_n);
    printf("Результат обчислення C(x={1,0}, a_n={0}): %s\n", res ? "TRUE (1)" : "FALSE (0)");

    circuit_free(c);
    return 0;
}
