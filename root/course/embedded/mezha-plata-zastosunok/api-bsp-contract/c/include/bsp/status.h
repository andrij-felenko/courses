#ifndef BSP_STATUS_H
#define BSP_STATUS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Статуси повернення функцій BSP.
 *
 * Єдиний перелік на весь контракт: застосунок ухвалює рішення про стратегію
 * відновлення, не заглядаючи у вендорні регістри помилок мікроконтролера.
 */
typedef enum {
    BSP_STATUS_OK                 =  0, /**< Операцію виконано успішно */
    BSP_STATUS_ERR_INVALID_PARAM  = -1, /**< Некоректний покажчик або значення аргументу */
    BSP_STATUS_ERR_NOT_INIT       = -2, /**< Периферію або домен не було ініціалізовано */
    BSP_STATUS_ERR_BUSY           = -3, /**< Апаратна шина зайнята іншою транзакцією */
    BSP_STATUS_ERR_TIMEOUT        = -4, /**< Закінчився час очікування апаратної відповіді */
    BSP_STATUS_ERR_BUS_FAULT      = -5, /**< Апаратна помилка шини (NACK, лінія затиснута в 0) */
    BSP_STATUS_ERR_POWER_FAULT    = -6, /**< Збій живлення або неприпустима просадка напруги */
    BSP_STATUS_ERR_UNSUPPORTED    = -7  /**< Операція недоступна в цьому контексті чи на цій ревізії плати */
} bsp_status_t;

/**
 * @brief Короткий текст статусу для системного логера.
 * @return Незмінний рядок; ніколи не NULL.
 */
const char *bsp_status_str(bsp_status_t status);

/** Раннє повернення з функції, якщо вкладений виклик не дав BSP_STATUS_OK. */
#define BSP_TRY(expr)                                   \
    do {                                                \
        const bsp_status_t bsp_try_st_ = (expr);        \
        if (bsp_try_st_ != BSP_STATUS_OK) {             \
            return bsp_try_st_;                         \
        }                                               \
    } while (0)

#ifdef __cplusplus
}
#endif

#endif /* BSP_STATUS_H */
