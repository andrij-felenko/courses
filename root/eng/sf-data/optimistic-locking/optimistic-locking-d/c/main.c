#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Результат виконання SQL-команди */
typedef struct {
    int64_t affected_rows;
    bool has_error;
    char error_msg[128];
} SqlExecResult;

/* Структура складського запису */
typedef struct {
    char sku[64];
    int32_t available_stock;
    int32_t reserved_stock;
    uint64_t lock_version;
} InventoryItem;

/* Імітація виклику інтерфейсу бази даних */
SqlExecResult execute_inventory_update(const char *sku, int32_t qty, uint64_t expected_version);
bool fetch_inventory_item(const char *sku, InventoryItem *out_item);

/* Функція резервування товару з оптимістичною перевіркою */
bool reserve_stock_optimistic(const char *sku, int32_t reserve_qty) {
    InventoryItem item;
    
    // 1. Читання стану без блокування СУБД
    if (!fetch_inventory_item(sku, &item)) {
        fprintf(stderr, "Помилка: товар %s не знайдено\n", sku);
        return false;
    }

    // 2. Перевірка бізнес-інваріанту в пам'яті
    if (item.available_stock < reserve_qty) {
        fprintf(stderr, "Брак залишків: доступно %d, запитано %d\n", 
                item.available_stock, reserve_qty);
        return false;
    }

    // 3. Атомарна спроба CAS-модифікації
    SqlExecResult res = execute_inventory_update(sku, reserve_qty, item.lock_version);
    
    if (res.has_error) {
        fprintf(stderr, "Системна помилка СУБД: %s\n", res.error_msg);
        return false;
    }

    // 4. Перевірка кількості змінених рядків
    if (res.affected_rows == 0) {
        // Колізія: рядок було змінено паралельною транзакцією
        fprintf(stderr, "Колізія версії для SKU %s (очікувалась версія %lu)\n", 
                sku, item.lock_version);
        return false; // Сигнал для запуску повторної спроби (Retry)
    }

    printf("Успішно зарезервовано %d шт. для товару %s\n", reserve_qty, sku);
    return true;
}
