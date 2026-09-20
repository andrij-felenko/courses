#ifndef FULFILLMENT_SERVICE_H
#define FULFILLMENT_SERVICE_H

#include "order_fulfillment_port.h"

/**
 * @file fulfillment_service.h
 * @brief Доменний сценарій пакетного виконання замовлень (Use Case Service).
 *
 * Сервіс реалізує чисту бізнес-логіку обробки замовлень:
 * 1. Запитує чергову партію через вихідний рольовий порт за доменним лімітом.
 * 2. Перевіряє інваріанти бізнес-правил для кожного замовлення.
 * 3. Затверджує замовлення зі зміною статусу на FULFILLED, або відхиляє його
 *    зі статусом CANCELLED у разі порушення інваріантів.
 * 4. Зберігає результати через рольовий порт.
 *
 * Зверніть увагу: сервіс не має жодної інформації про SQLite, зв'язні списки,
 * файлову систему, мережу чи транзакційні прапорці.
 */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Статистика результатів пакетної обробки замовлень.
 */
typedef struct {
    size_t total_processed; /**< Загальна кількість замовлень у партії */
    size_t fulfilled_count; /**< Кількість успішно виконаних замовлень */
    size_t cancelled_count; /**< Кількість скасованих через помилки інваріантів */
    size_t error_count;     /**< Кількість системних збоїв збереження через порт */
} fulfillment_batch_stats_t;

/**
 * @brief Структура бізнес-сервісу виконання замовлень.
 */
typedef struct {
    order_fulfillment_port_t *port; /**< Залежність: вихідний рольовий порт */
    size_t default_batch_size;      /**< Стандартний ліміт замовлень для однієї партії */
} fulfillment_service_t;

/**
 * @brief Ініціалізує сервіс виконання замовлень із впровадженням вихідного порту.
 *
 * @param service Покажчик на виділену пам'ять сервісу.
 * @param port Впроваджений контракт вихідного порту (Dependency Injection).
 * @param default_batch_size Розмір партії замовлень за замовчуванням.
 */
void fulfillment_service_init(fulfillment_service_t *service,
                              order_fulfillment_port_t *port,
                              size_t default_batch_size);

/**
 * @brief Виконує обробку чергової партії замовлень.
 *
 * @param service Покажчик на екземпляр сервісу.
 * @param batch_limit Бажана кількість замовлень (0 — використати default_batch_size).
 * @param out_stats Структура для запису підсумкової статистики обробки.
 * @return port_status_t Підсумковий статус виконання сценарію.
 */
port_status_t fulfillment_service_process_batch(fulfillment_service_t *service,
                                                size_t batch_limit,
                                                fulfillment_batch_stats_t *out_stats);

/**
 * @brief Перевіряє доменні інваріанти замовлення.
 *
 * Інваріанти:
 * - Ідентифікатор замовлення, клієнта та SKU не повинні бути порожніми.
 * - Кількість товару повинна бути більшою за 0.
 * - Загальна сума замовлення повинна перевищувати 0.00.
 *
 * @param order Покажчик на замовлення.
 * @return true Якщо всі бізнес-правила дотримано.
 * @return false Якщо хоча б один інваріант порушено.
 */
bool fulfillment_service_validate_order(const order_t *order);

#ifdef __cplusplus
}
#endif

#endif /* FULFILLMENT_SERVICE_H */
