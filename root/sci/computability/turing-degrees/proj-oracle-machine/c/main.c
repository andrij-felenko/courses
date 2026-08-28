#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_TAPE_SIZE 1024
#define MAX_STEPS 1000

/* --- Структури даних для C-реалізації --- */

typedef struct {
    uint8_t *elements;
    size_t capacity;
} finite_oracle_t;

typedef struct {
    size_t query_count;
    uint32_t queries[MAX_TAPE_SIZE];
    bool responses[MAX_TAPE_SIZE];
    uint32_t max_queried_value;
} query_log_t;

typedef enum {
    STATE_RUNNING,
    STATE_HALTED,
    STATE_STEP_LIMIT_EXCEEDED
} machine_status_t;

typedef struct {
    int tape[MAX_TAPE_SIZE];
    size_t head_pos;
    size_t query_tape[MAX_TAPE_SIZE];
    size_t query_len;
    machine_status_t status;
    size_t steps_executed;
    query_log_t log;
} otm_state_t;

/* Створення та ініціалізація оракула */
finite_oracle_t* oracle_create(size_t capacity) {
    finite_oracle_t *oracle = (finite_oracle_t*)malloc(sizeof(finite_oracle_t));
    if (!oracle) return NULL;
    oracle->elements = (uint8_t*)calloc(capacity, sizeof(uint8_t));
    oracle->capacity = capacity;
    return oracle;
}

void oracle_free(finite_oracle_t *oracle) {
    if (oracle) {
        free(oracle->elements);
        free(oracle);
    }
}

void oracle_add(finite_oracle_t *oracle, uint32_t value) {
    if (oracle && value < oracle->capacity) {
        oracle->elements[value] = 1;
    }
}

bool oracle_query(const finite_oracle_t *oracle, uint32_t value, query_log_t *log) {
    bool result = false;
    if (oracle && value < oracle->capacity) {
        result = (oracle->elements[value] == 1);
    }
    if (log && log->query_count < MAX_TAPE_SIZE) {
        log->queries[log->query_count] = value;
        log->responses[log->query_count] = result;
        if (value > log->max_queried_value) {
            log->max_queried_value = value;
        }
        log->query_count++;
    }
    return result;
}

/* Ініціалізація оракульної машини */
void otm_init(otm_state_t *machine) {
    memset(machine->tape, 0, sizeof(machine->tape));
    machine->head_pos = MAX_TAPE_SIZE / 2;
    machine->query_len = 0;
    machine->status = STATE_RUNNING;
    machine->steps_executed = 0;
    machine->log.query_count = 0;
    machine->log.max_queried_value = 0;
}

/* Симуляція виконання алгоритму з оракулом:
   Приклад програми: обчислити x + 1, якщо x ∈ B; інакше 0 */
void otm_run_example(otm_state_t *machine, const finite_oracle_t *oracle, uint32_t input_x) {
    otm_init(machine);
    
    /* Запис входження x на стрічку запиту */
    machine->query_tape[0] = input_x;
    machine->query_len = 1;
    machine->steps_executed++;

    /* Запит до оракула B */
    bool in_oracle = oracle_query(oracle, input_x, &machine->log);
    machine->steps_executed++;

    /* Прийняття рішення за результатом запиту */
    if (in_oracle) {
        machine->tape[machine->head_pos] = (int)input_x + 1;
    } else {
        machine->tape[machine->head_pos] = 0;
    }
    
    machine->status = STATE_HALTED;
}

/* Симуляція стрибка Тюринга (A') для перших N машин на оракулі A */
void compute_turing_jump_approximation(const finite_oracle_t *oracle, size_t num_machines) {
    printf("=== Симуляція Стрибка Тюринга (A') ===\n");
    for (size_t m = 0; m < num_machines; ++m) {
        otm_state_t machine;
        /* Перевірка зупинки машини 'm' на власному індексі */
        otm_run_example(&machine, oracle, (uint32_t)m);
        
        bool halted = (machine.status == STATE_HALTED);
        size_t use_func = machine.log.max_queried_value + 1;
        
        printf("Машина M_%zu^A(%zu): %s | Кроків: %zu | Стрибок A' ∈ [%s] | Використання u(%zu) = %zu\n",
               m, m,
               halted ? "ЗУПИНИЛАСЯ" : "РОЗБІГАЄТЬСЯ",
               machine.steps_executed,
               halted ? "ТАК" : "НІ",
               m, use_func);
    }
}

int main(void) {
    /* Створення оракула A = {1, 3, 7, 12} */
    finite_oracle_t *oracle_A = oracle_create(64);
    oracle_add(oracle_A, 1);
    oracle_add(oracle_A, 3);
    oracle_add(oracle_A, 7);
    oracle_add(oracle_A, 12);

    compute_turing_jump_approximation(oracle_A, 5);

    oracle_free(oracle_A);
    return 0;
}
