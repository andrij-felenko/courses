#ifndef SQLITE_FULFILLMENT_ADAPTER_H
#define SQLITE_FULFILLMENT_ADAPTER_H

#include "order_fulfillment_port.h"
#include <stdbool.h>

/**
 * @file sqlite_fulfillment_adapter.h
 * @brief Промисловий вторинний адаптер сховища на базі реляційної СКБД SQLite.
 *
 * Адаптер повністю інкапсулює:
 * 1. Дескриптор бази даних sqlite3.
 * 2. Скомпільовані підготовлені вирази (prepared statements).
 * 3. Локальне керування транзакціями (BEGIN IMMEDIATE, COMMIT, ROLLBACK).
 * 4. SQL-запити з обмеженням вибірки (LIMIT ?) та мапінг колонок таблиці в доменну структуру.
 *
 * Жодна деталь реляційного рушія не виходить назовні крізь рольовий контракт порту.
 */

#ifdef __cplusplus
extern "C" {
#endif

typedef struct sqlite3 sqlite3;
typedef struct sqlite3_stmt sqlite3_stmt;

/**
 * @brief Внутрішня контекстна структура SQLite-адаптера.
 */
typedef struct sqlite_fulfillment_adapter {
    order_fulfillment_port_t port;  /**< Реалізований контракт рольового вихідного порту */
    sqlite3 *db;                    /**< Дескриптор відкритого з'єднання SQLite */
    sqlite3_stmt *stmt_fetch;       /**< Підготовлений вираз для вибірки чергової партії */
    sqlite3_stmt *stmt_update;      /**< Підготовлений вираз для зміни статусу замовлення */
    bool is_initialized;            /**< Ознака коректної ініціалізації дескрипторів */
} sqlite_fulfillment_adapter_t;

/**
 * @brief Відкриває базу даних (файлову або in-memory ":memory:") та готує SQL-вирази.
 *
 * @param adapter Покажчик на виділену структуру адаптера.
 * @param db_path Шлях до файлу бази даних або ":memory:".
 * @return true Якщо базу успішно відкрито та підготовлено.
 * @return false При помилці відкриття чи підготовки SQL.
 */
bool sqlite_fulfillment_adapter_init(sqlite_fulfillment_adapter_t *adapter, const char *db_path);

/**
 * @brief Створює таблицю orders та супровідні індекси, якщо вони ще не існують.
 *
 * @param adapter Покажчик на адаптер.
 * @return true Якщо схему успішно створено.
 * @return false При синтаксичній чи дисковій помилці SQL.
 */
bool sqlite_fulfillment_adapter_create_table(sqlite_fulfillment_adapter_t *adapter);

/**
 * @brief Допоміжна функція адаптера для вставки тестових даних у реляційну таблицю.
 *
 * @param adapter Покажчик на адаптер.
 * @param order Доменне замовлення для запису в таблицю.
 * @return true При успішній вставці.
 * @return false При помилці SQL.
 */
bool sqlite_fulfillment_adapter_insert_order(sqlite_fulfillment_adapter_t *adapter, const order_t *order);

/**
 * @brief Допоміжна функція інспекції поточного стану замовлення безпосередньо з таблиці.
 *
 * @param adapter Покажчик на адаптер.
 * @param order_id Ідентифікатор замовлення.
 * @param out_order Структура для запису вичитаного замовлення.
 * @return true Якщо замовлення знайдено.
 * @return false Якщо запис відсутній у базі даних.
 */
bool sqlite_fulfillment_adapter_get_order(sqlite_fulfillment_adapter_t *adapter,
                                          const char *order_id,
                                          order_t *out_order);

/**
 * @brief Повертає контракт вихідного рольового порту для передачі в доменне ядро.
 *
 * @param adapter Покажчик на адаптер.
 * @return order_fulfillment_port_t* Покажчик на контракт порту.
 */
order_fulfillment_port_t *sqlite_fulfillment_adapter_get_port(sqlite_fulfillment_adapter_t *adapter);

/**
 * @brief Закриває підготовлені вирази та дескриптор SQLite, звільняючи виділені ресурси.
 *
 * @param adapter Покажчик на адаптер.
 */
void sqlite_fulfillment_adapter_destroy(sqlite_fulfillment_adapter_t *adapter);

#ifdef __cplusplus
}
#endif

#endif /* SQLITE_FULFILLMENT_ADAPTER_H */
