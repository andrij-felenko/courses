#ifndef MEM_FULFILLMENT_ADAPTER_H
#define MEM_FULFILLMENT_ADAPTER_H

#include "order_fulfillment_port.h"
#include <stdbool.h>

/**
 * @file mem_fulfillment_adapter.h
 * @brief Тестовий in-memory двійник вихідного порту (In-Memory Test Fake).
 *
 * Реалізує той самий контракт order_fulfillment_port_t на основі динамічного
 * зв'язного списку в оперативній пам'яті.
 *
 * Переваги для тестування (на противагу важким мокам або дисковим базам):
 * 1. Жодного зв'язку з SQLite або дисковими файлами.
 * 2. Детермінованість та блискавична швидкість виконання модульних тестів.
 * 3. Повноцінна імітація збереження стану без крихких перевірок конкретних SQL-викликів.
 */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Вузол зв'язного списку замовлень у пам'яті.
 */
typedef struct mem_order_node {
    order_t order;                 /**< Копія доменного замовлення */
    struct mem_order_node *next;   /**< Покажчик на наступний вузол */
} mem_order_node_t;

/**
 * @brief Контекст тестового двійника в пам'яті.
 */
typedef struct mem_fulfillment_adapter {
    order_fulfillment_port_t port; /**< Експортований контракт рольового порту */
    mem_order_node_t *head;        /**< Початок зв'язного списку */
    size_t count;                  /**< Загальна кількість замовлень у сховищі */
} mem_fulfillment_adapter_t;

/**
 * @brief Ініціалізує двійник у пам'яті порожнім списком.
 *
 * @param adapter Покажчик на структуру адаптера.
 */
void mem_fulfillment_adapter_init(mem_fulfillment_adapter_t *adapter);

/**
 * @brief Додає замовлення у внутрішній зв'язний список (для наповнення тестового контексту).
 *
 * @param adapter Покажчик на адаптер.
 * @param order Доменне замовлення для додавання.
 * @return true Якщо вузол успішно виділено й додано.
 * @return false При нестачі пам'яті або некоректних аргументах.
 */
bool mem_fulfillment_adapter_add_order(mem_fulfillment_adapter_t *adapter, const order_t *order);

/**
 * @brief Отримує замовлення за ідентифікатором (для верифікації стану в тестах).
 *
 * @param adapter Покажчик на адаптер.
 * @param order_id Ідентифікатор замовлення.
 * @param out_order Покажчик для збереження знайденого замовлення.
 * @return true Якщо знайдено.
 * @return false Якщо замовлення відсутнє.
 */
bool mem_fulfillment_adapter_get_order(const mem_fulfillment_adapter_t *adapter,
                                       const char *order_id,
                                       order_t *out_order);

/**
 * @brief Повертає покажчик на контракт рольового порту для інжекції в сервіс.
 *
 * @param adapter Покажчик на адаптер.
 * @return order_fulfillment_port_t* Покажчик на інтерфейс порту.
 */
order_fulfillment_port_t *mem_fulfillment_adapter_get_port(mem_fulfillment_adapter_t *adapter);

/**
 * @brief Звільняє всі виділені вузли зв'язного списку.
 *
 * @param adapter Покажчик на адаптер.
 */
void mem_fulfillment_adapter_destroy(mem_fulfillment_adapter_t *adapter);

#ifdef __cplusplus
}
#endif

#endif /* MEM_FULFILLMENT_ADAPTER_H */
