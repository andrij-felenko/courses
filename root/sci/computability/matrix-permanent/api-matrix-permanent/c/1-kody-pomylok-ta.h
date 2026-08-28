#ifndef MATRIX_PERM_H
#define MATRIX_PERM_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Коди повернення та статус виконання */
typedef enum {
    PERM_SUCCESS             =  0,  /**< Обчислення завершено успішно */
    PERM_ERR_NULL_POINTER    = -1,  /**< Передано нульовий вказівник на матрицю або результат */
    PERM_ERR_INVALID_DIM     = -2,  /**< Некоректна розмірність матриці (n == 0 або n > 62) */
    PERM_ERR_OUT_OF_MEMORY   = -3,  /**< Помилка виділення динамічної пам'яті */
    PERM_ERR_OVERFLOW        = -4,  /**< Виявлено неконтрольоване переповнення для знакового типу */
    PERM_ERR_UNSUPPORTED_ALG = -5   /**< Обрано непідтримуваний алгоритм обчислення */
} perm_status_t;

/** Алгоритм обчислення перманента */
typedef enum {
    PERM_ALG_AUTO            = 0,  /**< Автоматичний вибір кращого алгоритму за розмірністю */
    PERM_ALG_NAIVE           = 1,  /**< Наївний перебір перестановок O(n! · n) */
    PERM_ALG_RYSER_GRAY      = 2,  /**< Формула Райзера з кодом Ґрея O(2ⁿ · n) */
    PERM_ALG_GLYNN           = 3   /**< Алгоритм Ґлінна з векторами знаків O(2ⁿ⁻¹ · n) */
} perm_algorithm_t;

/** Конфігурація параметрів обчислення */
typedef struct {
    perm_algorithm_t algorithm;   /**< Обраний алгоритм */
    size_t           num_threads; /**< Кількість потоків (0 для автовизначення) */
    bool             use_simd;    /**< Прапорець використання SIMD інструкцій */
} perm_config_t;

#ifdef __cplusplus
}
#endif

#endif /* MATRIX_PERM_H */
