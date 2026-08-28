/* c — Симулятор схем AC0 та генератор обмежень на C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum { GATE_INPUT, GATE_NOT, GATE_AND, GATE_OR } GateType;

typedef struct {
    size_t id;
    GateType type;
    size_t input_var; /* Для GATE_INPUT */
    size_t* fan_in;   /* Масив ID вхідних гейтів (unbounded fan-in) */
    size_t fan_in_count;
    uint8_t value;
} Gate;

typedef struct {
    size_t num_inputs;
    size_t num_gates;
    Gate* gates;
    size_t output_gate_id;
} Circuit;

Circuit* circuit_create(size_t num_inputs, size_t max_gates) {
    Circuit* c = (Circuit*)malloc(sizeof(Circuit));
    c->num_inputs = num_inputs;
    c->num_gates = 0;
    c->gates = (Gate*)calloc(max_gates, sizeof(Gate));
    c->output_gate_id = 0;
    return c;
}

size_t circuit_add_input(Circuit* c, size_t var_idx) {
    size_t id = c->num_gates++;
    c->gates[id].id = id;
    c->gates[id].type = GATE_INPUT;
    c->gates[id].input_var = var_idx;
    return id;
}

size_t circuit_add_gate(Circuit* c, GateType type, const size_t* inputs, size_t count) {
    size_t id = c->num_gates++;
    c->gates[id].id = id;
    c->gates[id].type = type;
    c->gates[id].fan_in_count = count;
    c->gates[id].fan_in = (size_t*)malloc(count * sizeof(size_t));
    memcpy(c->gates[id].fan_in, inputs, count * sizeof(size_t));
    return id;
}

uint8_t circuit_eval(Circuit* c, const uint8_t* in_vec) {
    for (size_t i = 0; i < c->num_gates; ++i) {
        Gate* g = &c->gates[i];
        if (g->type == GATE_INPUT) {
            g->value = in_vec[g->input_var];
        } else if (g->type == GATE_NOT) {
            g->value = !c->gates[g->fan_in[0]].value;
        } else if (g->type == GATE_AND) {
            uint8_t res = 1;
            for (size_t j = 0; j < g->fan_in_count; ++j) {
                if (!c->gates[g->fan_in[j]].value) { res = 0; break; }
            }
            g->value = res;
        } else if (g->type == GATE_OR) {
            uint8_t res = 0;
            for (size_t j = 0; j < g->fan_in_count; ++j) {
                if (c->gates[g->fan_in[j]].value) { res = 1; break; }
            }
            g->value = res;
        }
    }
    return c->gates[c->output_gate_id].value;
}

void circuit_free(Circuit* c) {
    for (size_t i = 0; i < c->num_gates; ++i) {
        free(c->gates[i].fan_in);
    }
    free(c->gates);
    free(c);
}

int main(void) {
    size_t n = 4;
    Circuit* c = circuit_create(n, 32);
    size_t in_ids[4];
    for (size_t i = 0; i < n; ++i) in_ids[i] = circuit_add_input(c, i);

    /* Побудова спрощеного шару OR над AND для перших 2 бітів */
    size_t and1 = circuit_add_gate(c, GATE_AND, (size_t[]){in_ids[0], in_ids[1]}, 2);
    size_t out = circuit_add_gate(c, GATE_OR, (size_t[]){and1, in_ids[2]}, 2);
    c->output_gate_id = out;

    uint8_t input_val[4] = {1, 1, 0, 0};
    uint8_t res = circuit_eval(c, input_val);
    printf("Результат оцінки схеми AC0: %d\n", res);

    circuit_free(c);
    return 0;
}
