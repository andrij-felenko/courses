#include "fulfillment_service.h"
#include <stdio.h>
#include <string.h>

#define MAX_BATCH_CAPACITY 128

void fulfillment_service_init(fulfillment_service_t *service,
                              order_fulfillment_port_t *port,
                              size_t default_batch_size)
{
    if (!service) {
        return;
    }
    service->port = port;
    service->default_batch_size = (default_batch_size > 0) ? default_batch_size : 10;
}

bool fulfillment_service_validate_order(const order_t *order)
{
    if (!order) {
        return false;
    }

    /* Інваріант 1: обов'язкові доменні ідентифікатори */
    if (order->id[0] == '\0' || order->customer_id[0] == '\0' || order->item_sku[0] == '\0') {
        return false;
    }

    /* Інваріант 2: кількість товару має бути строго додатною */
    if (order->quantity == 0) {
        return false;
    }

    /* Інваріант 3: вартість замовлення має бути додатною */
    if (order->total_amount <= 0.0) {
        return false;
    }

    return true;
}

port_status_t fulfillment_service_process_batch(fulfillment_service_t *service,
                                                size_t batch_limit,
                                                fulfillment_batch_stats_t *out_stats)
{
    if (!service || !service->port) {
        return PORT_STATUS_ERR_INVALID_ARG;
    }

    if (out_stats) {
        memset(out_stats, 0, sizeof(*out_stats));
    }

    size_t limit = (batch_limit > 0) ? batch_limit : service->default_batch_size;
    if (limit > MAX_BATCH_CAPACITY) {
        limit = MAX_BATCH_CAPACITY;
    }

    order_t batch[MAX_BATCH_CAPACITY];
    size_t count = 0;

    /* 1. Доменний запит чергової партії через рольовий порт.
     * Зверніть увагу: ядро не передає зміщення сторінок (offset), номер сторінки чи SQL-фільтри.
     * Запитується суто партія готових до обробки замовлень за критерієм розміру. */
    port_status_t status = order_fulfillment_port_fetch_pending(service->port, limit, batch, &count);
    if (status != PORT_STATUS_OK) {
        printf("[Доменний сервіс] Помилка вибірки партії замовлень через порт: %s\n",
               port_status_to_string(status));
        return status;
    }

    if (count == 0) {
        printf("[Доменний сервіс] Немає замовлень у стані PENDING для обробки.\n");
        return PORT_STATUS_OK;
    }

    printf("[Доменний сервіс] Отримано партію з %zu замовлень для обробки.\n", count);

    /* 2. Обробка кожного замовлення відповідно до бізнес-правил */
    for (size_t i = 0; i < count; i++) {
        order_t *order = &batch[i];
        bool is_valid = fulfillment_service_validate_order(order);

        order_status_t target_status = is_valid ? ORDER_STATUS_FULFILLED : ORDER_STATUS_CANCELLED;

        printf("  -> Замовлення %s: клієнт=%s, товар=%s, к-ть=%u, сума=%.2f -> %s (%s)\n",
               order->id,
               order->customer_id,
               order->item_sku,
               order->quantity,
               order->total_amount,
               is_valid ? "СХВАЛЕНО ДО ВИКОНАННЯ" : "ВІДХИЛЕНО (порушення інваріантів)",
               order_status_to_string(target_status));

        /* 3. Збереження результату обробки через рольовий порт.
         * Домен не знає, чи виконується тут SQL UPDATE, чи оновлення вузла зв'язного списку. */
        port_status_t upd_status = order_fulfillment_port_update_status(service->port, order->id, target_status);

        if (out_stats) {
            out_stats->total_processed++;
            if (upd_status == PORT_STATUS_OK) {
                if (is_valid) {
                    out_stats->fulfilled_count++;
                } else {
                    out_stats->cancelled_count++;
                }
            } else {
                out_stats->error_count++;
                printf("  [!] Помилка оновлення статусу замовлення %s: %s\n",
                       order->id, port_status_to_string(upd_status));
            }
        }
    }

    return PORT_STATUS_OK;
}
