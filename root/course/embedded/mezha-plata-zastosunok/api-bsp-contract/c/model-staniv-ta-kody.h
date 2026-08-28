#ifndef BSP_STATUS_H
#define BSP_STATUS_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Статуси повернення функцій BSP.
 */
typedef enum {
    BSP_STATUS_OK                 =  0, /**< Операцію виконано успішно */
    BSP_STATUS_ERR_INVALID_PARAM  = -1, /**< Некоректний покажчик або значення аргументу */
    BSP_STATUS_ERR_NOT_INIT       = -2, /**< Периферію або домен не було ініціалізовано */
    BSP_STATUS_ERR_BUSY           = -3, /**< Апаратна шина зайнята іншою транзакцією */
    BSP_STATUS_ERR_TIMEOUT        = -4, /**< Закінчився час очікування апаратної відповіді */
    BSP_STATUS_ERR_BUS_FAULT      = -5, /**< Апаратна помилка шини (NACK, лінія затиснута в 0) */
    BSP_STATUS_ERR_POWER_FAULT    = -6, /**< Збій живлення або неприпустима просадка напруги */
    BSP_STATUS_ERR_UNSUPPORTED    = -7  /**< Операція не підтримується поточною ревізією плати */
} bsp_status_t;

#endif /* BSP_STATUS_H */
