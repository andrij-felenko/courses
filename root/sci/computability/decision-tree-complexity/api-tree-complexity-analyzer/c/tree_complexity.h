/* C API: tree_complexity.h */
#ifndef TREE_COMPLEXITY_H
#define TREE_COMPLEXITY_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Типи помилок */
typedef enum {
    TC_SUCCESS              =  0,
    TC_ERR_INVALID_N        = -1,
    TC_ERR_NULL_POINTER     = -2,
    TC_ERR_TABLE_SIZE       = -3,
    TC_ERR_OUT_OF_MEMORY    = -4,
    TC_ERR_TIMEOUT          = -5
} tc_error_t;

/* Прапорці обчислення для вибіркового аналізу метрик */
typedef enum {
    TC_OPT_NONE             = 0x00,
    TC_OPT_SENSITIVITY      = 0x01,  /* Обчислити s(f) */
    TC_OPT_BLOCK_SENSITIVITY= 0x02,  /* Обчислити bs(f) */
    TC_OPT_CERTIFICATE      = 0x04,  /* Обчислити C(f) */
    TC_OPT_DEGREE           = 0x08,  /* Обчислити deg(f) */
    TC_OPT_DECISION_TREE    = 0x10,  /* Обчислити D(f) */
    TC_OPT_ALL              = 0x1F   /* Обчислити всі метрики */
} tc_options_t;

/* Структура результатів аналізу */
typedef struct {
    uint32_t num_variables;      /* Кількість змінних n */
    uint32_t sensitivity;        /* Проста чутливість s(f) */
    uint32_t block_sensitivity;  /* Блокова чутливість bs(f) */
    uint32_t cert_complexity_0;  /* Складність 0-сертифіката C0(f) */
    uint32_t cert_complexity_1;  /* Складність 1-сертифіката C1(f) */
    uint32_t cert_complexity;    /* Загальна складність сертифікатів C(f) */
    uint32_t degree;             /* Степінь многочлена deg(f) */
    uint32_t decision_tree_depth;/* Детермінована складність D(f) */
    double   execution_time_ms;  /* Час виконання у мілісекундах */
} tc_result_t;

/* Створення контексту булевої функції та обчислення обраних метрик */
tc_error_t tc_analyze_truth_table(
    uint32_t num_vars,
    const uint8_t *truth_table,
    uint32_t options,
    tc_result_t *out_result
);

/* Отримання текстового опису помилки */
const char* tc_error_string(tc_error_t err);

#ifdef __cplusplus
}
#endif

#endif /* TREE_COMPLEXITY_H */
