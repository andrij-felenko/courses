#include "sqlite_fulfillment_adapter.h"
#include <sqlite3.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * @brief Транслює доменний статус замовлення в текстове представлення стовпця таблиці.
 */
static const char *status_to_sql_string(order_status_t status) {
    switch (status) {
        case ORDER_STATUS_PENDING:   return "PENDING";
        case ORDER_STATUS_FULFILLED: return "FULFILLED";
        case ORDER_STATUS_CANCELLED: return "CANCELLED";
        default:                     return "UNKNOWN";
    }
}

/**
 * @brief Транслює текстове значення стовпця таблиці у доменний статус замовлення.
 */
static order_status_t status_from_sql_string(const char *str) {
    if (!str) {
        return ORDER_STATUS_PENDING;
    }
    if (strcmp(str, "FULFILLED") == 0) {
        return ORDER_STATUS_FULFILLED;
    }
    if (strcmp(str, "CANCELLED") == 0) {
        return ORDER_STATUS_CANCELLED;
    }
    return ORDER_STATUS_PENDING;
}

/**
 * @brief Реалізація методу вибірки партії замовлень рольового порту для SQLite.
 */
static port_status_t sqlite_adapter_fetch_pending(order_fulfillment_port_t *self,
                                                  size_t max_count,
                                                  order_t *out_orders,
                                                  size_t *out_count)
{
    if (!self || !self->ctx || !out_orders || !out_count) {
        return PORT_STATUS_ERR_INVALID_ARG;
    }

    sqlite_fulfillment_adapter_t *adapter = (sqlite_fulfillment_adapter_t *)self->ctx;
    *out_count = 0;

    if (!adapter->is_initialized || !adapter->stmt_fetch) {
        return PORT_STATUS_ERR_STORAGE;
    }

    if (max_count == 0) {
        return PORT_STATUS_OK;
    }

    sqlite3_reset(adapter->stmt_fetch);
    sqlite3_clear_bindings(adapter->stmt_fetch);

    /* Прив'язуємо доменний ліміт розміру партії до параметра SQL LIMIT ? */
    if (sqlite3_bind_int64(adapter->stmt_fetch, 1, (sqlite3_int64)max_count) != SQLITE_OK) {
        return PORT_STATUS_ERR_STORAGE;
    }

    while (sqlite3_step(adapter->stmt_fetch) == SQLITE_ROW && *out_count < max_count) {
        order_t *order = &out_orders[*out_count];
        memset(order, 0, sizeof(*order));

        const unsigned char *id_text = sqlite3_column_text(adapter->stmt_fetch, 0);
        const unsigned char *cust_text = sqlite3_column_text(adapter->stmt_fetch, 1);
        const unsigned char *sku_text = sqlite3_column_text(adapter->stmt_fetch, 2);
        int qty = sqlite3_column_int(adapter->stmt_fetch, 3);
        double amt = sqlite3_column_double(adapter->stmt_fetch, 4);
        const unsigned char *status_text = sqlite3_column_text(adapter->stmt_fetch, 5);

        if (id_text) {
            strncpy(order->id, (const char *)id_text, sizeof(order->id) - 1);
        }
        if (cust_text) {
            strncpy(order->customer_id, (const char *)cust_text, sizeof(order->customer_id) - 1);
        }
        if (sku_text) {
            strncpy(order->item_sku, (const char *)sku_text, sizeof(order->item_sku) - 1);
        }
        order->quantity = (qty > 0) ? (uint32_t)qty : 0;
        order->total_amount = amt;
        order->status = status_from_sql_string((const char *)status_text);

        (*out_count)++;
    }

    sqlite3_reset(adapter->stmt_fetch);
    return PORT_STATUS_OK;
}

/**
 * @brief Реалізація оновлення статусу замовлення рольового порту з локальною транзакцією.
 */
static port_status_t sqlite_adapter_update_status(order_fulfillment_port_t *self,
                                                  const char *order_id,
                                                  order_status_t new_status)
{
    if (!self || !self->ctx || !order_id) {
        return PORT_STATUS_ERR_INVALID_ARG;
    }

    sqlite_fulfillment_adapter_t *adapter = (sqlite_fulfillment_adapter_t *)self->ctx;
    if (!adapter->is_initialized || !adapter->stmt_update || !adapter->db) {
        return PORT_STATUS_ERR_STORAGE;
    }

    /* 1. Локальне керування транзакцією: адаптер починає транзакцію (BEGIN IMMEDIATE).
     * Доменний сервіс ніколи не бачить дескрипторів транзакцій чи SQL-інструкцій. */
    char *err_msg = NULL;
    int rc = sqlite3_exec(adapter->db, "BEGIN IMMEDIATE;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        if (err_msg) {
            sqlite3_free(err_msg);
        }
        return PORT_STATUS_ERR_CONCURRENCY;
    }

    sqlite3_reset(adapter->stmt_update);
    sqlite3_clear_bindings(adapter->stmt_update);

    const char *status_str = status_to_sql_string(new_status);
    sqlite3_bind_text(adapter->stmt_update, 1, status_str, -1, SQLITE_STATIC);
    sqlite3_bind_text(adapter->stmt_update, 2, order_id, -1, SQLITE_STATIC);

    rc = sqlite3_step(adapter->stmt_update);
    sqlite3_reset(adapter->stmt_update);

    if (rc != SQLITE_DONE) {
        /* При збої виконання операції виконуємо відкат (ROLLBACK) */
        sqlite3_exec(adapter->db, "ROLLBACK;", NULL, NULL, NULL);
        return PORT_STATUS_ERR_STORAGE;
    }

    /* Перевіряємо кількість реально змінених рядків */
    int changes = sqlite3_changes(adapter->db);
    if (changes == 0) {
        /* Якщо жодного рядка не оновлено, замовлення з таким ID не існує в базі */
        sqlite3_exec(adapter->db, "ROLLBACK;", NULL, NULL, NULL);
        return PORT_STATUS_ERR_NOT_FOUND;
    }

    /* 2. Фіксація транзакції (COMMIT) */
    rc = sqlite3_exec(adapter->db, "COMMIT;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        if (err_msg) {
            sqlite3_free(err_msg);
        }
        sqlite3_exec(adapter->db, "ROLLBACK;", NULL, NULL, NULL);
        return PORT_STATUS_ERR_STORAGE;
    }

    return PORT_STATUS_OK;
}

bool sqlite_fulfillment_adapter_init(sqlite_fulfillment_adapter_t *adapter, const char *db_path)
{
    if (!adapter || !db_path) {
        return false;
    }

    memset(adapter, 0, sizeof(*adapter));

    int rc = sqlite3_open(db_path, &adapter->db);
    if (rc != SQLITE_OK) {
        if (adapter->db) {
            sqlite3_close(adapter->db);
            adapter->db = NULL;
        }
        return false;
    }

    /* Підготовка скомпільованого виразу вибірки чергової партії замовлень у стані PENDING */
    const char *sql_fetch =
        "SELECT id, customer_id, item_sku, quantity, total_amount, status "
        "FROM orders WHERE status = 'PENDING' LIMIT ?;";

    rc = sqlite3_prepare_v2(adapter->db, sql_fetch, -1, &adapter->stmt_fetch, NULL);
    if (rc != SQLITE_OK) {
        sqlite3_close(adapter->db);
        adapter->db = NULL;
        return false;
    }

    /* Підготовка скомпільованого виразу оновлення статусу замовлення */
    const char *sql_update = "UPDATE orders SET status = ? WHERE id = ?;";
    rc = sqlite3_prepare_v2(adapter->db, sql_update, -1, &adapter->stmt_update, NULL);
    if (rc != SQLITE_OK) {
        sqlite3_finalize(adapter->stmt_fetch);
        adapter->stmt_fetch = NULL;
        sqlite3_close(adapter->db);
        adapter->db = NULL;
        return false;
    }

    adapter->port.ctx = adapter;
    adapter->port.fetch_pending_batch = sqlite_adapter_fetch_pending;
    adapter->port.update_status = sqlite_adapter_update_status;
    adapter->is_initialized = true;

    return true;
}

bool sqlite_fulfillment_adapter_create_table(sqlite_fulfillment_adapter_t *adapter)
{
    if (!adapter || !adapter->db) {
        return false;
    }

    const char *sql_ddl =
        "CREATE TABLE IF NOT EXISTS orders ("
        "    id TEXT PRIMARY KEY NOT NULL,"
        "    customer_id TEXT NOT NULL,"
        "    item_sku TEXT NOT NULL,"
        "    quantity INTEGER NOT NULL,"
        "    total_amount REAL NOT NULL,"
        "    status TEXT NOT NULL"
        ");"
        "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);";

    char *err_msg = NULL;
    int rc = sqlite3_exec(adapter->db, sql_ddl, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        if (err_msg) {
            sqlite3_free(err_msg);
        }
        return false;
    }

    return true;
}

bool sqlite_fulfillment_adapter_insert_order(sqlite_fulfillment_adapter_t *adapter, const order_t *order)
{
    if (!adapter || !adapter->db || !order) {
        return false;
    }

    const char *sql_insert =
        "INSERT OR REPLACE INTO orders (id, customer_id, item_sku, quantity, total_amount, status) "
        "VALUES (?, ?, ?, ?, ?, ?);";

    sqlite3_stmt *stmt = NULL;
    int rc = sqlite3_prepare_v2(adapter->db, sql_insert, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        return false;
    }

    sqlite3_bind_text(stmt, 1, order->id, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, order->customer_id, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 3, order->item_sku, -1, SQLITE_STATIC);
    sqlite3_bind_int(stmt, 4, (int)order->quantity);
    sqlite3_bind_double(stmt, 5, order->total_amount);
    sqlite3_bind_text(stmt, 6, status_to_sql_string(order->status), -1, SQLITE_STATIC);

    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return (rc == SQLITE_DONE);
}

bool sqlite_fulfillment_adapter_get_order(sqlite_fulfillment_adapter_t *adapter,
                                          const char *order_id,
                                          order_t *out_order)
{
    if (!adapter || !adapter->db || !order_id || !out_order) {
        return false;
    }

    const char *sql_select =
        "SELECT id, customer_id, item_sku, quantity, total_amount, status FROM orders WHERE id = ?;";

    sqlite3_stmt *stmt = NULL;
    int rc = sqlite3_prepare_v2(adapter->db, sql_select, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        return false;
    }

    sqlite3_bind_text(stmt, 1, order_id, -1, SQLITE_STATIC);

    bool found = false;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        memset(out_order, 0, sizeof(*out_order));
        const unsigned char *id_text = sqlite3_column_text(stmt, 0);
        const unsigned char *cust_text = sqlite3_column_text(stmt, 1);
        const unsigned char *sku_text = sqlite3_column_text(stmt, 2);
        int qty = sqlite3_column_int(stmt, 3);
        double amt = sqlite3_column_double(stmt, 4);
        const unsigned char *status_text = sqlite3_column_text(stmt, 5);

        if (id_text) {
            strncpy(out_order->id, (const char *)id_text, sizeof(out_order->id) - 1);
        }
        if (cust_text) {
            strncpy(out_order->customer_id, (const char *)cust_text, sizeof(out_order->customer_id) - 1);
        }
        if (sku_text) {
            strncpy(out_order->item_sku, (const char *)sku_text, sizeof(out_order->item_sku) - 1);
        }
        out_order->quantity = (qty > 0) ? (uint32_t)qty : 0;
        out_order->total_amount = amt;
        out_order->status = status_from_sql_string((const char *)status_text);
        found = true;
    }

    sqlite3_finalize(stmt);
    return found;
}

order_fulfillment_port_t *sqlite_fulfillment_adapter_get_port(sqlite_fulfillment_adapter_t *adapter)
{
    if (!adapter || !adapter->is_initialized) {
        return NULL;
    }
    return &adapter->port;
}

void sqlite_fulfillment_adapter_destroy(sqlite_fulfillment_adapter_t *adapter)
{
    if (!adapter) {
        return;
    }

    if (adapter->stmt_fetch) {
        sqlite3_finalize(adapter->stmt_fetch);
        adapter->stmt_fetch = NULL;
    }

    if (adapter->stmt_update) {
        sqlite3_finalize(adapter->stmt_update);
        adapter->stmt_update = NULL;
    }

    if (adapter->db) {
        sqlite3_close(adapter->db);
        adapter->db = NULL;
    }

    adapter->is_initialized = false;
}
