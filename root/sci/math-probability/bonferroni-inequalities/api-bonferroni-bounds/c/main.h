#ifndef BONFERRONI_BOUNDS_H
#define BONFERRONI_BOUNDS_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Коди помилок виконання модуля */
typedef enum {
    BONFERRONI_OK                   =  0,
    BONFERRONI_ERR_INVALID_PARAM    = -1,
    BONFERRONI_ERR_OUT_OF_MEMORY    = -2,
    BONFERRONI_ERR_ORACLE_FAILURE   = -3,
    BONFERRONI_ERR_PRECISION_LOSS   = -4,
    BONFERRONI_ERR_BUFFER_TOO_SMALL = -5
} bonferroni_error_t;

/** Конфігураційні параметри для обчислення меж */
typedef struct {
    size_t max_order;           /* Максимальний порядок k (1..n) */
    double target_precision;    /* Бажаний допустимий зазор між межами (верхня - нижня) */
    bool enable_early_stop;     /* Зупинка обчислень при досягненні target_precision */
    uint32_t flags;             /* Прапори оптимізації (0 - за замовчуванням) */
} bonferroni_config_t;

/** Результат обчислення меж Бонферроні */
typedef struct {
    double upper_bound;         /* Оцінка зверху P(⋃ Aᵢ) <= upper_bound */
    double lower_bound;         /* Оцінка знизу P(⋃ Aᵢ) >= lower_bound */
    double confidence_gap;      /* Поточна різниця (upper_bound - lower_bound) */
    double* s_terms;            /* Масив розрахованих сум S_1, S_2 ... S_k (розмір max_order + 1) */
    size_t evaluated_order;     /* Фактично обчислений порядок k */
    bonferroni_error_t status;  /* Статус завершення */
} bonferroni_bounds_t;

/** Сигнатура оракула обчислення перетинів */
typedef double (*bonferroni_oracle_fn)(const size_t* event_indices, size_t count, void* context);

/**
 * Ініціалізація структури конфігурації за замовчуванням.
 */
void bonferroni_config_init(bonferroni_config_t* cfg);

/**
 * Обчислення обсягу оперативної пам'яті (у байтах), необхідного для виконання
 * обчислення для n подій та порядку max_k.
 */
size_t bonferroni_required_memory_bytes(size_t event_count, size_t max_k);

/**
 * Головна функція розрахунку меж Бонферроні.
 * 
 * @param event_count  Загальна кількість подій n (n >= 1)
 * @param oracle       Вказівник на функцію-оракул перетинів
 * @param context      Користувацький контекст для оракула
 * @param cfg          Конфігурація (якщо NULL, використовуються параметри за замовчуванням)
 * @param out_bounds   Вказівник на вихідну структуру результатів
 * @return BONFERRONI_OK у разі успіху, або код помилки
 */
bonferroni_error_t bonferroni_compute(
    size_t event_count,
    bonferroni_oracle_fn oracle,
    void* context,
    const bonferroni_config_t* cfg,
    bonferroni_bounds_t* out_bounds
);

/**
 * Звільнення ресурсів, виділених під структуру результатів.
 */
void bonferroni_bounds_free(bonferroni_bounds_t* bounds);

#ifdef __cplusplus
}
#endif

#endif /* BONFERRONI_BOUNDS_H */
