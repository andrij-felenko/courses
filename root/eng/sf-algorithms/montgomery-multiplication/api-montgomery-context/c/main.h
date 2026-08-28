#ifndef MONTGOMERY_API_H
#define MONTGOMERY_API_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/**
 * @brief Статуси виконання операцій контексту Монтгомері
 */
typedef enum {
    MONTGOMERY_OK               = 0,  /**< Успішне виконання */
    MONTGOMERY_ERR_INVALID_ARG  = -1, /**< Нульовий вказівник або некоректні розміри */
    MONTGOMERY_ERR_EVEN_MODULUS = -2, /**< Модуль N є парним (НСД(N, 2) != 1) */
    MONTGOMERY_ERR_ALLOC        = -3  /**< Помилка виділення динамічної пам'яті */
} montgomery_status_t;

/**
 * @brief Структура контексту Монтгомері
 */
typedef struct {
    size_t   k;        /**< Кількість 64-бітних лімбів модуля */
    uint64_t *n;       /**< Масив лімбів модуля N (розмір k) */
    uint64_t *r2;      /**< Константа R^2 mod N для входу в простір (розмір k) */
    uint64_t n0_prime; /**< Константа n0' = (-N[0]^(-1)) mod 2^64 */
    uint64_t *workspace; /**< Попередньо виділений робочий буфер (розмір k + 2) */
} montgomery_ctx_t;

/**
 * @brief Ініціалізація контексту Монтгомері
 * @param ctx Вказівник на структуру контексту
 * @param modulus Масив 64-бітних слів модуля (little-endian)
 * @param k Кількість слів у модулі
 * @return MONTGOMERY_OK у разі успіху, інакше код помилки
 */
montgomery_status_t montgomery_ctx_init(montgomery_ctx_t *ctx,
                                        const uint64_t *modulus,
                                        size_t k);

/**
 * @brief Звільнення ресурсів контексту
 * @param ctx Вказівник на контекст (пам'ять обнуляється)
 */
void montgomery_ctx_free(montgomery_ctx_t *ctx);

/**
 * @brief Переведення числа у форму Монтгомері: a_bar = (a * R) mod N
 * @param ctx Ініціалізований контекст
 * @param a Вхідне число в стандартному представленні (розмір k)
 * @param a_bar Вихідний буфер для образу Монтгомері (розмір k)
 */
montgomery_status_t montgomery_to_domain(const montgomery_ctx_t *ctx,
                                         const uint64_t *a,
                                         uint64_t *a_bar);

/**
 * @brief Зворотне переведення з форми Монтгомері: a = (a_bar * R^(-1)) mod N
 * @param ctx Ініціалізований контекст
 * @param a_bar Вхідне число у формі Монтгомері (розмір k)
 * @param a Вихідний буфер для стандартного числа (розмір k)
 */
montgomery_status_t montgomery_from_domain(const montgomery_ctx_t *ctx,
                                           const uint64_t *a_bar,
                                           uint64_t *a);

/**
 * @brief Множення у просторі Монтгомері: res_bar = (a_bar * b_bar * R^(-1)) mod N
 * @param ctx Ініціалізований контекст
 * @param a_bar Перший множник у формі Монтгомері (розмір k)
 * @param b_bar Другий множник у формі Монтгомері (розмір k)
 * @param res_bar Результат у формі Монтгомері (розмір k)
 */
montgomery_status_t montgomery_mul(const montgomery_ctx_t *ctx,
                                   const uint64_t *a_bar,
                                   const uint64_t *b_bar,
                                   uint64_t *res_bar);

/**
 * @brief Піднесення до квадрата у просторі Монтгомері: res_bar = (a_bar^2 * R^(-1)) mod N
 */
montgomery_status_t montgomery_sqr(const montgomery_ctx_t *ctx,
                                   const uint64_t *a_bar,
                                   uint64_t *res_bar);

/**
 * @brief Модулярне експоненціювання: res = (base^exp) mod N
 * @param ctx Ініціалізований контекст
 * @param base Основа в стандартному вигляді (розмір k)
 * @param exp Показник степеня (масив слів exp_limbs)
 * @param exp_limbs Кількість слів у показнику степеня
 * @param res Результат у стандартному вигляді (розмір k)
 */
montgomery_status_t montgomery_exp(const montgomery_ctx_t *ctx,
                                   const uint64_t *base,
                                   const uint64_t *exp,
                                   size_t exp_limbs,
                                   uint64_t *res);

#endif /* MONTGOMERY_API_H */
