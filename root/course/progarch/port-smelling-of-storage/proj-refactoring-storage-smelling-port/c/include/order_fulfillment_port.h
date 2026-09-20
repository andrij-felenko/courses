#ifndef ORDER_FULFILLMENT_PORT_H
#define ORDER_FULFILLMENT_PORT_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/**
 * @file order_fulfillment_port.h
 * @brief Абстрактний контракт вихідного рольового порту (Egress / Outbound Port).
 *
 * У гексагональній архітектурі вихідний порт проєктується ВИКЛЮЧНО від потреб
 * бізнес-сценарію (Role-based Interface / Inside-Out Design).
 *
 * Антипатерн «Порт, що пахне сховищем» (Port smelling of storage):
 * - Загальні CRUD-сигнатури (save, findById, delete).
 * - Витік деталей реляційної СКБД: пагінація сторінками (pageNumber, pageSize, offset),
 *   сортування за іменами колонок ("created_at DESC"), прапорці блокування рядків
 *   (isForUpdate), типи сторонніх бібліотек чи SQL-дескриптори.
 *
 * Чисте рішення:
 * - Порт містить лише методи, потрібні конкретному сценарію виконання:
 *   отримати чергову партію замовлень, готових до обробки (fetch_pending_batch),
 *   та зберегти змінений статус конкретного замовлення (update_status).
 * - Жодних SQL-запитів, зв'язків з базою даних, транзакційних прапорців СКБД.
 */

#ifdef __cplusplus
extern "C" {
#endif

#define ORDER_ID_MAX_LEN       32
#define ORDER_CUSTOMER_MAX_LEN 32
#define ORDER_SKU_MAX_LEN      32

/**
 * @brief Доменні статуси життєвого циклу замовлення.
 */
typedef enum {
    ORDER_STATUS_PENDING = 0,    /**< Замовлення очікує перевірки та виконання */
    ORDER_STATUS_FULFILLED = 1,  /**< Успішно виконане (списано залишки, оформлено доставку) */
    ORDER_STATUS_CANCELLED = 2   /**< Скасоване через порушення доменних інваріантів */
} order_status_t;

/**
 * @brief Доменні коди результатів викликів рольового порту.
 *
 * Абстраговані від помилок мережі, SQL-кодів повернення або блокувань СКБД.
 */
typedef enum {
    PORT_STATUS_OK = 0,               /**< Операцію успішно виконано */
    PORT_STATUS_ERR_INVALID_ARG = 1,  /**< Передано некоректні параметри або NULL-покажчик */
    PORT_STATUS_ERR_NOT_FOUND = 2,    /**< Замовлення з таким ідентифікатором не знайдено */
    PORT_STATUS_ERR_STORAGE = 3,      /**< Технічний збій рівня збереження */
    PORT_STATUS_ERR_CONCURRENCY = 4   /**< Конкурентний конфлікт блокування ресурсу */
} port_status_t;

/**
 * @brief Отримує рядкове представлення статусу замовлення для логування.
 */
static inline const char *order_status_to_string(order_status_t status) {
    switch (status) {
        case ORDER_STATUS_PENDING:   return "PENDING";
        case ORDER_STATUS_FULFILLED: return "FULFILLED";
        case ORDER_STATUS_CANCELLED: return "CANCELLED";
        default:                     return "UNKNOWN";
    }
}

/**
 * @brief Отримує рядкове представлення статусу порту для діагностики.
 */
static inline const char *port_status_to_string(port_status_t status) {
    switch (status) {
        case PORT_STATUS_OK:              return "PORT_STATUS_OK";
        case PORT_STATUS_ERR_INVALID_ARG: return "PORT_STATUS_ERR_INVALID_ARG";
        case PORT_STATUS_ERR_NOT_FOUND:   return "PORT_STATUS_ERR_NOT_FOUND";
        case PORT_STATUS_ERR_STORAGE:     return "PORT_STATUS_ERR_STORAGE";
        case PORT_STATUS_ERR_CONCURRENCY: return "PORT_STATUS_ERR_CONCURRENCY";
        default:                          return "PORT_STATUS_ERR_UNKNOWN";
    }
}

/**
 * @brief Доменна сутність замовлення.
 *
 * Оперує виключно бізнес-атрибутами, без системних табличних полів на кшталт
 * auto-increment id, rowversion, created_by_fk тощо.
 */
typedef struct {
    char id[ORDER_ID_MAX_LEN];                /**< Доменний унікальний номер замовлення */
    char customer_id[ORDER_CUSTOMER_MAX_LEN]; /**< Ідентифікатор клієнта */
    char item_sku[ORDER_SKU_MAX_LEN];         /**< Артикул товару */
    uint32_t quantity;                        /**< Кількість одиниць товару */
    double total_amount;                      /**< Загальна сума замовлення */
    order_status_t status;                    /**< Поточний стан замовлення */
} order_t;

typedef struct order_fulfillment_port order_fulfillment_port_t;

/**
 * @brief Контракт рольового вихідного порту виконання замовлень.
 *
 * Реалізований як структура покажчиків на функції з непрозорим контекстом ctx.
 * Це забезпечує поліморфізм мовою C без залежності ядра від конкретного адаптера.
 */
struct order_fulfillment_port {
    void *ctx; /**< Непрозорий покажчик на стан конкретного адаптера (SQLite, in-memory тощо) */

    /**
     * @brief Запитує партію замовлень у стані PENDING, що потребують обробки.
     *
     * @param self Покажчик на контракт порту.
     * @param max_count Максимальна кількість замовлень у партії (доменний ліміт).
     * @param out_orders Масив для запису отриманих замовлень.
     * @param out_count Кількість реально поміщених у масив замовлень.
     * @return port_status_t Результат вибірки.
     */
    port_status_t (*fetch_pending_batch)(order_fulfillment_port_t *self,
                                         size_t max_count,
                                         order_t *out_orders,
                                         size_t *out_count);

    /**
     * @brief Оновлює статус замовлення в сховищі за його ідентифікатором.
     *
     * @param self Покажчик на контракт порту.
     * @param order_id Доменний ідентифікатор замовлення.
     * @param new_status Новий доменний статус.
     * @return port_status_t Результат оновлення.
     */
    port_status_t (*update_status)(order_fulfillment_port_t *self,
                                   const char *order_id,
                                   order_status_t new_status);
};

/**
 * @brief Безпечний виклик вибірки партії через порт.
 */
static inline port_status_t order_fulfillment_port_fetch_pending(
    order_fulfillment_port_t *port,
    size_t max_count,
    order_t *out_orders,
    size_t *out_count)
{
    if (!port || !port->fetch_pending_batch) {
        return PORT_STATUS_ERR_INVALID_ARG;
    }
    return port->fetch_pending_batch(port, max_count, out_orders, out_count);
}

/**
 * @brief Безпечний виклик оновлення статусу через порт.
 */
static inline port_status_t order_fulfillment_port_update_status(
    order_fulfillment_port_t *port,
    const char *order_id,
    order_status_t new_status)
{
    if (!port || !port->update_status) {
        return PORT_STATUS_ERR_INVALID_ARG;
    }
    return port->update_status(port, order_id, new_status);
}

#ifdef __cplusplus
}
#endif

#endif /* ORDER_FULFILLMENT_PORT_H */
