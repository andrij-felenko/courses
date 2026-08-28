#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

/* Структура для представлення стану детермінованої машини M_i */
typedef struct {
    int id;
    int poly_degree;
    bool (*simulate_func)(const char* input);
} TuringMachine;

/* Структура для представлення зведення R_i */
typedef struct {
    int id;
    int poly_degree;
    void (*reduce_func)(const char* input, char* output_buf, size_t buf_size);
} Reduction;

/* Спрощена імітація контрольного ящика SAT */
static bool oracle_sat(const char* input) {
    if (!input || strlen(input) == 0) return false;
    /* Символічна умова здійсненності: сума ASCII парна */
    size_t sum = 0;
    for (size_t i = 0; input[i] != '\0'; ++i) {
        sum += (unsigned char)input[i];
    }
    return (sum % 2 == 0);
}

/* Імітація хибного алгоритму M_i (помиляється на деякій довжині) */
static bool dummy_machine_0(const char* input) {
    (void)input;
    return true; /* Завжди каже true -> помилиться на сумі непарній */
}

/* Імітація хибного зведення R_i */
static void dummy_reduction_0(const char* input, char* output_buf, size_t buf_size) {
    (void)input;
    snprintf(output_buf, buf_size, ""); /* Порожній рядок */
}

/* Обчислення мови Леднера A(x) за допомогою значення H(|x|) */
static bool eval_ladner_language(const char* input, int h_val) {
    if (h_val % 2 != 0) {
        /* Непарна фаза: A поводиться як порожня мова */
        return false;
    }
    /* Парна фаза: A поводиться як SAT */
    return oracle_sat(input);
}

/* Діагностичний крок симулятора Леднера */
typedef struct {
    int h_value;
    unsigned long steps_used;
    bool phase_switched;
} SimulationResult;

SimulationResult run_ladner_step(int n, int prev_h) {
    SimulationResult res;
    res.h_value = prev_h;
    res.steps_used = 0;
    res.phase_switched = false;

    unsigned long budget = (unsigned long)n * n * n;
    int phase = prev_h;
    int candidate_idx = phase / 2;

    char test_input[64];

    if (phase % 2 == 0) {
        /* Парна фаза: спростування приналежності до P для M_{candidate_idx} */
        TuringMachine m = { candidate_idx, 2, dummy_machine_0 };

        for (int len = 1; len <= n; ++len) {
            snprintf(test_input, sizeof(test_input), "test_str_%d", len);
            
            bool m_res = m.simulate_func(test_input);
            bool true_a = eval_ladner_language(test_input, prev_h);
            
            res.steps_used += (unsigned long)(len * len);

            if (res.steps_used > budget) {
                break; /* Перевищено часовий бюджет n^3 */
            }

            if (m_res != true_a) {
                /* Знайдено контрекземпляр! Переключаємо фазу */
                res.h_value = prev_h + 1;
                res.phase_switched = true;
                return res;
            }
        }
    } else {
        /* Непарна фаза: спростування NP-повноти для зведення R_{candidate_idx} */
        Reduction r = { candidate_idx, 2, dummy_reduction_0 };
        char red_out[64];

        for (int len = 1; len <= n; ++len) {
            snprintf(test_input, sizeof(test_input), "sat_formula_%d", len);
            
            r.reduce_func(test_input, red_out, sizeof(red_out));
            bool is_sat = oracle_sat(test_input);
            bool target_in_a = eval_ladner_language(red_out, prev_h);

            res.steps_used += (unsigned long)(len * len);

            if (res.steps_used > budget) {
                break;
            }

            if (is_sat != target_in_a) {
                /* Спростовано зведення! Переключаємо фазу */
                res.h_value = prev_h + 1;
                res.phase_switched = true;
                return res;
            }
        }
    }

    return res;
}

int main(void) {
    printf("=== ДІАГНОСТИЧНИЙ СИМУЛЯТОР ЛЕДНЕРА (C) ===\n");
    int current_h = 0;

    for (int n = 1; n <= 10; ++n) {
        SimulationResult r = run_ladner_step(n, current_h);
        printf("Довжина входу n = %2d | Часовий бюджет = %4d | Kроки = %3lu | H(n) = %d %s\n",
               n, n * n * n, r.steps_used, r.h_value,
               r.phase_switched ? "[ПЕРЕКЛЮЧЕННЯ ФАЗИ!]" : "");
        current_h = r.h_value;
    }

    return 0;
}
