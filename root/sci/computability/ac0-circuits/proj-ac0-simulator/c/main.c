/* c — Симулятор схем AC0, генератор прискореного переносу та випадкових обмежень на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

typedef enum {
    GATE_INPUT = 0,
    GATE_NOT   = 1,
    GATE_AND   = 2,
    GATE_OR    = 3
} GateType;

typedef struct {
    size_t id;
    GateType type;
    size_t input_var;   /* Для GATE_INPUT: індекс вхідної змінної */
    size_t* fan_in;     /* Масив ID вхідних вентилів */
    size_t fan_in_count;
    uint8_t value;      /* Обчислене значення біта (0 або 1) */
} Gate;

typedef struct {
    size_t num_inputs;
    size_t num_gates;
    size_t max_gates;
    Gate* gates;
    size_t output_gate_id;
} Circuit;

Circuit* circuit_create(size_t num_inputs, size_t max_gates) {
    Circuit* c = (Circuit*)malloc(sizeof(Circuit));
    c->num_inputs = num_inputs;
    c->num_gates = 0;
    c->max_gates = max_gates;
    c->gates = (Gate*)calloc(max_gates, sizeof(Gate));
    c->output_gate_id = 0;
    return c;
}

size_t circuit_add_input(Circuit* c, size_t var_idx) {
    if (c->num_gates >= c->max_gates) return (size_t)-1;
    size_t id = c->num_gates++;
    c->gates[id].id = id;
    c->gates[id].type = GATE_INPUT;
    c->gates[id].input_var = var_idx;
    c->gates[id].fan_in = NULL;
    c->gates[id].fan_in_count = 0;
    return id;
}

size_t circuit_add_gate(Circuit* c, GateType type, const size_t* inputs, size_t count) {
    if (c->num_gates >= c->max_gates) return (size_t)-1;
    size_t id = c->num_gates++;
    c->gates[id].id = id;
    c->gates[id].type = type;
    c->gates[id].fan_in_count = count;
    c->gates[id].fan_in = (size_t*)malloc(count * sizeof(size_t));
    memcpy(c->gates[id].fan_in, inputs, count * sizeof(size_t));
    return id;
}

uint8_t circuit_eval(Circuit* c, const uint8_t* input_vector) {
    for (size_t i = 0; i < c->num_gates; ++i) {
        Gate* g = &c->gates[i];
        switch (g->type) {
            case GATE_INPUT:
                g->value = input_vector[g->input_var];
                break;
            case GATE_NOT:
                g->value = !c->gates[g->fan_in[0]].value;
                break;
            case GATE_AND: {
                uint8_t res = 1;
                for (size_t j = 0; j < g->fan_in_count; ++j) {
                    if (!c->gates[g->fan_in[j]].value) {
                        res = 0;
                        break; /* Закорочення / Насичення AND */
                    }
                }
                g->value = res;
                break;
            }
            case GATE_OR: {
                uint8_t res = 0;
                for (size_t j = 0; j < g->fan_in_count; ++j) {
                    if (c->gates[g->fan_in[j]].value) {
                        res = 1;
                        break; /* Закорочення / Насичення OR */
                    }
                }
                g->value = res;
                break;
            }
        }
    }
    return c->gates[c->output_gate_id].value;
}

/* Генератор випадкового обмеження rho in R_p */
void apply_random_restriction(size_t num_inputs, double p, int8_t* restriction) {
    for (size_t i = 0; i < num_inputs; ++i) {
        double r = (double)rand() / RAND_MAX;
        if (r < p) {
            restriction[i] = -1; /* Змінна вільна (*) */
        } else {
            restriction[i] = (rand() % 2 == 0) ? 0 : 1;
        }
    }
}

void circuit_free(Circuit* c) {
    if (!c) return;
    for (size_t i = 0; i < c->num_gates; ++i) {
        free(c->gates[i].fan_in);
    }
    free(c->gates);
    free(c);
}

int main(void) {
    srand((unsigned int)time(NULL));
    size_t n = 4;
    Circuit* c = circuit_create(n, 64);

    size_t in[4];
    for (size_t i = 0; i < n; ++i) in[i] = circuit_add_input(c, i);

    /* Побудова блоку додавання 2 бітів із прискореним переносом (AC0 схема глибини 3) */
    size_t g0 = circuit_add_gate(c, GATE_AND, (size_t[]){in[0], in[1]}, 2);
    size_t p0 = circuit_add_gate(c, GATE_OR,  (size_t[]){in[0], in[1]}, 2);
    size_t out = circuit_add_gate(c, GATE_OR, (size_t[]){g0, p0}, 2);
    c->output_gate_id = out;

    uint8_t test_input[4] = {1, 0, 1, 1};
    uint8_t res = circuit_eval(c, test_input);
    printf("Результат оцінки схеми C: %d\n", res);

    int8_t restriction[4];
    apply_random_restriction(n, 0.5, restriction);
    printf("Випадкове обмеження rho: ");
    for (size_t i = 0; i < n; ++i) {
        if (restriction[i] == -1) printf("* ");
        else printf("%d ", restriction[i]);
    }
    printf("\n");

    circuit_free(c);
    return 0;
}
