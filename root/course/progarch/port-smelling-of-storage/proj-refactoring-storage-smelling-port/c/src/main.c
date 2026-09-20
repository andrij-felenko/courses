#include "fulfillment_service.h"
#include "mem_fulfillment_adapter.h"
#include "sqlite_fulfillment_adapter.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

/**
 * @file main.c
 * @brief Корінь композиції (Composition Root) системи виконання замовлень.
 *
 * Демонструє:
 * 1. Запуск сценарію виконання замовлень із тестовим двійником у пам'яті (In-Memory Fake)
 *    для швидкої детермінованої перевірки бізнес-інваріантів без жодної СКБД.
 * 2. Запуск того самого сценарію виконання замовлень із промисловим SQLite-адаптером,
 *    який інкапсулює SQL-запити, ліміт вибірки та локальні транзакції.
 * 3. Повну відсутність змін у доменному сервісі: ядро взаємодіє виключно
 *    через абстрактний рольовий порт order_fulfillment_port_t.
 */

static void print_banner(const char *title) {
    printf("\n======================================================================\n");
    printf("  %s\n", title);
    printf("======================================================================\n");
}

/**
 * @brief Демонстрація модульного тестування домену за допомогою двійника в пам'яті.
 */
static void run_in_memory_suite(void) {
    print_banner("Етап 1: Швидкі модульні тести з In-Memory двійником (Fake)");
    printf("[Тест] Створення двійника в пам'яті на базі зв'язного списку...\n");

    mem_fulfillment_adapter_t mem_adapter;
    mem_fulfillment_adapter_init(&mem_adapter);

    /* Тестові замовлення: валідні та з порушенням інваріантів */
    order_t o1 = { "ORD-001", "CUST-10", "LAPTOP-X", 1, 1250.00, ORDER_STATUS_PENDING };
    order_t o2 = { "ORD-002", "CUST-20", "MOUSE-BT", 0,   35.00, ORDER_STATUS_PENDING }; /* Помилка: к-ть = 0 */
    order_t o3 = { "ORD-003", "CUST-30", "KB-MECH",  2,  -80.00, ORDER_STATUS_PENDING }; /* Помилка: сума <= 0 */
    order_t o4 = { "ORD-004", "CUST-40", "MON-4K",   2,  890.00, ORDER_STATUS_PENDING }; /* Валідне */

    mem_fulfillment_adapter_add_order(&mem_adapter, &o1);
    mem_fulfillment_adapter_add_order(&mem_adapter, &o2);
    mem_fulfillment_adapter_add_order(&mem_adapter, &o3);
    mem_fulfillment_adapter_add_order(&mem_adapter, &o4);

    /* Ініціалізуємо доменний сценарій, передаючи абстрактний інтерфейс порту */
    fulfillment_service_t service;
    fulfillment_service_init(&service, mem_fulfillment_adapter_get_port(&mem_adapter), 10);

    fulfillment_batch_stats_t stats;
    port_status_t status = fulfillment_service_process_batch(&service, 10, &stats);

    printf("\n[Тест] Результати пакетної обробки (In-Memory):\n");
    printf("  Оброблено: %zu, Виконано: %zu, Скасовано: %zu, Помилок: %zu\n",
           stats.total_processed, stats.fulfilled_count, stats.cancelled_count, stats.error_count);

    assert(status == PORT_STATUS_OK);
    assert(stats.total_processed == 4);
    assert(stats.fulfilled_count == 2);
    assert(stats.cancelled_count == 2);
    assert(stats.error_count == 0);

    /* Верифікація збереженого стану замовлень */
    order_t check_order;
    assert(mem_fulfillment_adapter_get_order(&mem_adapter, "ORD-001", &check_order) && check_order.status == ORDER_STATUS_FULFILLED);
    assert(mem_fulfillment_adapter_get_order(&mem_adapter, "ORD-002", &check_order) && check_order.status == ORDER_STATUS_CANCELLED);
    assert(mem_fulfillment_adapter_get_order(&mem_adapter, "ORD-003", &check_order) && check_order.status == ORDER_STATUS_CANCELLED);
    assert(mem_fulfillment_adapter_get_order(&mem_adapter, "ORD-004", &check_order) && check_order.status == ORDER_STATUS_FULFILLED);

    printf("[Тест] Усі перевірки бізнес-інваріантів успішно пройдено без створення файлів БД!\n");

    mem_fulfillment_adapter_destroy(&mem_adapter);
}

/**
 * @brief Демонстрація промислового адаптера з персистентністю в SQLite.
 */
static void run_sqlite_suite(void) {
    print_banner("Етап 2: Промисловий SQLite-адаптер (інкапсуляція SQL та транзакцій)");
    printf("[SQLite] Ініціалізація адаптера бази даних (in-memory ':memory:')...\n");

    sqlite_fulfillment_adapter_t sqlite_adapter;
    bool ok = sqlite_fulfillment_adapter_init(&sqlite_adapter, ":memory:");
    if (!ok) {
        printf("[!] Помилка: не вдалося відкрити SQLite-адаптер.\n");
        return;
    }

    sqlite_fulfillment_adapter_create_table(&sqlite_adapter);

    /* Наповнення бази даних початковими замовленнями у стані PENDING */
    order_t db_o1 = { "ORD-SQL-101", "CORP-ALPHA", "SRV-RACK", 2, 4500.00, ORDER_STATUS_PENDING };
    order_t db_o2 = { "ORD-SQL-102", "CORP-BETA",  "SW-48PORT", 4, 1800.00, ORDER_STATUS_PENDING };
    order_t db_o3 = { "ORD-SQL-103", "CORP-GAMMA", "PATCH-CAT", 0,   50.00, ORDER_STATUS_PENDING }; /* Невалідне (к-ть 0) */

    sqlite_fulfillment_adapter_insert_order(&sqlite_adapter, &db_o1);
    sqlite_fulfillment_adapter_insert_order(&sqlite_adapter, &db_o2);
    sqlite_fulfillment_adapter_insert_order(&sqlite_adapter, &db_o3);

    /* Той самий доменний сценарій підключається до SQLite-порту без жодних правок у коді ядра */
    fulfillment_service_t service;
    fulfillment_service_init(&service, sqlite_fulfillment_adapter_get_port(&sqlite_adapter), 2);

    /* Обробка партії 1: ліміт 2 замовлення (адаптер виконає SQL LIMIT 2) */
    printf("\n--- Обробка першої партії (ліміт = 2) ---\n");
    fulfillment_batch_stats_t stats1;
    fulfillment_service_process_batch(&service, 2, &stats1);

    /* Обробка партії 2: ліміт 2 замовлення (вибірка наступних замовлень у стані PENDING) */
    printf("\n--- Обробка другої партії (ліміт = 2) ---\n");
    fulfillment_batch_stats_t stats2;
    fulfillment_service_process_batch(&service, 2, &stats2);

    /* Верифікація стану рядків у реляційній таблиці */
    printf("\n[SQLite] Верифікація фіксації статусів у реляційній таблиці:\n");
    order_t row;
    if (sqlite_fulfillment_adapter_get_order(&sqlite_adapter, "ORD-SQL-101", &row)) {
        printf("  ORD-SQL-101 -> статус: %s (очікується FULFILLED)\n", order_status_to_string(row.status));
        assert(row.status == ORDER_STATUS_FULFILLED);
    }
    if (sqlite_fulfillment_adapter_get_order(&sqlite_adapter, "ORD-SQL-102", &row)) {
        printf("  ORD-SQL-102 -> статус: %s (очікується FULFILLED)\n", order_status_to_string(row.status));
        assert(row.status == ORDER_STATUS_FULFILLED);
    }
    if (sqlite_fulfillment_adapter_get_order(&sqlite_adapter, "ORD-SQL-103", &row)) {
        printf("  ORD-SQL-103 -> статус: %s (очікується CANCELLED)\n", order_status_to_string(row.status));
        assert(row.status == ORDER_STATUS_CANCELLED);
    }

    printf("[SQLite] Усі транзакції успішно зафіксовано в реляційній базі даних!\n");

    sqlite_fulfillment_adapter_destroy(&sqlite_adapter);
}

int main(void) {
    print_banner("Демонстрація архітектури: Вихідний рольовий порт без запаху сховища");
    printf("Доменний сервіс (fulfillment_service) взаємодіє виключно з рольовим\n");
    printf("контрактом order_fulfillment_port_t, не маючи жодного знання про СКБД.\n");

    run_in_memory_suite();
    run_sqlite_suite();

    print_banner("Підсумок: Доменне ядро повністю захищене від витоку деталей збереження!");
    return 0;
}
