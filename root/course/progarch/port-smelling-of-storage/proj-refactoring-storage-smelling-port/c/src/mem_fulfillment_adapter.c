#include "mem_fulfillment_adapter.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/**
 * @brief Вибірка замовлень у стані PENDING із пам'яті за доменним лімітом.
 */
static port_status_t mem_adapter_fetch_pending(order_fulfillment_port_t *self,
                                               size_t max_count,
                                               order_t *out_orders,
                                               size_t *out_count)
{
    if (!self || !self->ctx || !out_orders || !out_count) {
        return PORT_STATUS_ERR_INVALID_ARG;
    }

    mem_fulfillment_adapter_t *adapter = (mem_fulfillment_adapter_t *)self->ctx;
    *out_count = 0;

    if (max_count == 0) {
        return PORT_STATUS_OK;
    }

    mem_order_node_t *curr = adapter->head;
    while (curr && *out_count < max_count) {
        if (curr->order.status == ORDER_STATUS_PENDING) {
            out_orders[*out_count] = curr->order;
            (*out_count)++;
        }
        curr = curr->next;
    }

    return PORT_STATUS_OK;
}

/**
 * @brief Оновлення статусу замовлення у зв'язному списку пам'яті.
 */
static port_status_t mem_adapter_update_status(order_fulfillment_port_t *self,
                                               const char *order_id,
                                               order_status_t new_status)
{
    if (!self || !self->ctx || !order_id) {
        return PORT_STATUS_ERR_INVALID_ARG;
    }

    mem_fulfillment_adapter_t *adapter = (mem_fulfillment_adapter_t *)self->ctx;
    mem_order_node_t *curr = adapter->head;

    while (curr) {
        if (strcmp(curr->order.id, order_id) == 0) {
            curr->order.status = new_status;
            return PORT_STATUS_OK;
        }
        curr = curr->next;
    }

    return PORT_STATUS_ERR_NOT_FOUND;
}

void mem_fulfillment_adapter_init(mem_fulfillment_adapter_t *adapter)
{
    if (!adapter) {
        return;
    }
    memset(adapter, 0, sizeof(*adapter));
    adapter->port.ctx = adapter;
    adapter->port.fetch_pending_batch = mem_adapter_fetch_pending;
    adapter->port.update_status = mem_adapter_update_status;
    adapter->head = NULL;
    adapter->count = 0;
}

bool mem_fulfillment_adapter_add_order(mem_fulfillment_adapter_t *adapter, const order_t *order)
{
    if (!adapter || !order) {
        return false;
    }

    mem_order_node_t *node = (mem_order_node_t *)malloc(sizeof(mem_order_node_t));
    if (!node) {
        return false;
    }

    node->order = *order;
    node->next = NULL;

    /* Додаємо в кінець списку для збереження хронологічного порядку надходження */
    if (!adapter->head) {
        adapter->head = node;
    } else {
        mem_order_node_t *curr = adapter->head;
        while (curr->next) {
            curr = curr->next;
        }
        curr->next = node;
    }
    adapter->count++;

    return true;
}

bool mem_fulfillment_adapter_get_order(const mem_fulfillment_adapter_t *adapter,
                                       const char *order_id,
                                       order_t *out_order)
{
    if (!adapter || !order_id || !out_order) {
        return false;
    }

    mem_order_node_t *curr = adapter->head;
    while (curr) {
        if (strcmp(curr->order.id, order_id) == 0) {
            *out_order = curr->order;
            return true;
        }
        curr = curr->next;
    }

    return false;
}

order_fulfillment_port_t *mem_fulfillment_adapter_get_port(mem_fulfillment_adapter_t *adapter)
{
    if (!adapter) {
        return NULL;
    }
    return &adapter->port;
}

void mem_fulfillment_adapter_destroy(mem_fulfillment_adapter_t *adapter)
{
    if (!adapter) {
        return;
    }

    mem_order_node_t *curr = adapter->head;
    while (curr) {
        mem_order_node_t *next = curr->next;
        free(curr);
        curr = next;
    }

    adapter->head = NULL;
    adapter->count = 0;
}
