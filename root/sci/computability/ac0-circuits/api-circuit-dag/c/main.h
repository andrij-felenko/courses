/* c — Публічний C-інтерфейс бібліотеки libac0circuit */
#ifndef LIBAC0_CIRCUIT_H
#define LIBAC0_CIRCUIT_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    AC0_GATE_INPUT = 0,
    AC0_GATE_NOT   = 1,
    AC0_GATE_AND   = 2,
    AC0_GATE_OR    = 3
} ac0_gate_type_t;

typedef struct ac0_gate_t {
    size_t id;
    ac0_gate_type_t type;
    size_t var_index;       /* Тільки для AC0_GATE_INPUT */
    size_t* fan_in_ids;     /* Масив ідентифікаторів вхідних гейтів */
    size_t fan_in_count;
    size_t fan_out_count;   /* Кількість вихідних ребер */
    size_t layer;           /* Рівень гейта у графі (0 для входів) */
} ac0_gate_t;

typedef struct ac0_circuit_t {
    size_t num_inputs;
    size_t num_gates;
    size_t max_gates;
    ac0_gate_t* gates;
    size_t output_gate_id;
    size_t computed_depth;  /* Кешована глибина схеми */
} ac0_circuit_t;

typedef struct ac0_fanin_stats_t {
    size_t max_fan_in;
    size_t min_fan_in;
    double avg_fan_in;
    size_t max_fan_out;
} ac0_fanin_stats_t;

/* Функції створення та вилучення */
ac0_circuit_t* ac0_circuit_create(size_t num_inputs, size_t initial_capacity);
void ac0_circuit_destroy(ac0_circuit_t* circuit);

/* Функції конструювання графа */
size_t ac0_circuit_add_input(ac0_circuit_t* circuit, size_t var_index);
size_t ac0_circuit_add_gate(ac0_circuit_t* circuit, ac0_gate_type_t type, const size_t* inputs, size_t count);
bool ac0_circuit_set_output(ac0_circuit_t* circuit, size_t gate_id);

/* Аналітичні функції */
size_t ac0_circuit_get_depth(ac0_circuit_t* circuit);
size_t ac0_circuit_get_size(ac0_circuit_t* circuit);
ac0_fanin_stats_t ac0_circuit_get_stats(const ac0_circuit_t* circuit);

/* Валідація критеріїв AC0 */
bool ac0_circuit_validate(const ac0_circuit_t* circuit, size_t max_allowed_depth, size_t max_allowed_size);

/* Обчислення значення */
uint8_t ac0_circuit_evaluate(const ac0_circuit_t* circuit, const uint8_t* input_bits, size_t input_len);

#ifdef __cplusplus
}
#endif

#endif /* LIBAC0_CIRCUIT_H */
