#ifndef GF256_API_H
#define GF256_API_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/**
 * @brief Коди повернення та статусів виконання операцій API
 */
typedef enum {
    GF_SUCCESS              =  0,  /**< Операцію виконано успішно */
    GF_ERR_NULL_POINTER     = -1,  /**< Передано нульовий вказівник у критичний параметр */
    GF_ERR_DIVISION_BY_ZERO = -2,  /**< Спроба ділення на нуль або інверсії нуля */
    GF_ERR_INVALID_POLY     = -3,  /**< Заданий многочлен не є незвідним */
    GF_ERR_OUT_OF_BOUNDS    = -4,  /**< Значення параметра виходить за межі поля */
    GF_ERR_NOT_INITIALIZED  = -5   /**< Таблиці або контекст не були ініціалізовані */
} gf_status_t;

/**
 * @brief Контекст розширеного поля GF(2^m) для розрядності m <= 64
 */
typedef struct {
    uint64_t poly;           /**< Незвідний многочлен (без старшого біта x^m) */
    uint64_t field_size;     /**< Загальна кількість елементів q = 2^m */
    uint64_t poly_mask;      /**< Бітова маска нижніх m бітів (2^m - 1) */
    uint8_t  m;              /**< Степінь розширення поля (1..64) */
    bool     is_primitive;   /**< Прапор примітивності заданого полінома */
} gf2m_context_t;

/**
 * @brief Предобчислені таблиці логарифмів та експонент для GF(2^8)
 */
typedef struct {
    uint8_t exp_table[512];  /**< Таблиця експонент (продубльована для запобігання mod 255) */
    uint8_t log_table[256];  /**< Таблиця дискретних логарифмів */
    bool    initialized;     /**< Прапор готовності таблиць до роботи */
} gf256_tables_t;

#endif /* GF256_API_H */
