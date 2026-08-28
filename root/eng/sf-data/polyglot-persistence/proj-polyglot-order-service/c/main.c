#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ORDERS 64
#define MAX_EVENTS 128
#define MAX_CACHE 64
#define STR_LEN 64

typedef struct {
    int id;
    char customer[STR_LEN];
    double amount;
    char status[16];
    uint64_t version;
} order_record_t;

typedef struct {
    int event_id;
    int order_id;
    char event_type[32];
    char payload[128];
    uint64_t version;
    bool processed;
} outbox_event_t;

typedef struct {
    int order_id;
    char cached_data[128];
    uint64_t version;
} cache_entry_t;

typedef struct {
    // 1. Primary OLTP Database
    order_record_t orders[MAX_ORDERS];
    size_t order_count;
    outbox_event_t outbox[MAX_EVENTS];
    size_t outbox_count;

    // 2. Key-Value Cache
    cache_entry_t cache[MAX_CACHE];
    size_t cache_count;
} polyglot_system_t;

void polyglot_init(polyglot_system_t *sys) {
    sys->order_count = 0;
    sys->outbox_count = 0;
    sys->cache_count = 0;
}

// Атомарне створення замовлення та запис в Outbox (ACID транзакція)
int create_order_transaction(polyglot_system_t *sys, int order_id, const char *customer, double amount) {
    if (sys->order_count >= MAX_ORDERS || sys->outbox_count >= MAX_EVENTS) return -1;

    // 1. Запис замовлення
    order_record_t *ord = &sys->orders[sys->order_count++];
    ord->id = order_id;
    strncpy(ord->customer, customer, STR_LEN - 1);
    ord->amount = amount;
    strncpy(ord->status, "CREATED", 15);
    ord->version = 1;

    // 2. Атомарний запис події в Outbox в тій самій транзакції
    outbox_event_t *ev = &sys->outbox[sys->outbox_count++];
    ev->event_id = (int)sys->outbox_count;
    ev->order_id = order_id;
    ev->version = 1;
    strncpy(ev->event_type, "ORDER_CREATED", 31);
    snprintf(ev->payload, 127, "{\"id\":%d,\"customer\":\"%s\",\"amount\":%.2f}", order_id, customer, amount);
    ev->processed = false;

    return 0;
}

// Фоновий процес обробки Outbox та синхронізації з Key-Value кешем
void process_outbox_events(polyglot_system_t *sys) {
    for (size_t i = 0; i < sys->outbox_count; ++i) {
        if (!sys->outbox[i].processed) {
            int oid = sys->outbox[i].order_id;
            uint64_t ver = sys->outbox[i].version;

            // Оновлення Key-Value кешу з перевіркою версії (Optimistic Locking)
            bool found_in_cache = false;
            for (size_t c = 0; c < sys->cache_count; ++c) {
                if (sys->cache[c].order_id == oid) {
                    if (ver >= sys->cache[c].version) {
                        strncpy(sys->cache[c].cached_data, sys->outbox[i].payload, 127);
                        sys->cache[c].version = ver;
                    }
                    found_in_cache = true;
                    break;
                }
            }

            if (!found_in_cache && sys->cache_count < MAX_CACHE) {
                sys->cache[sys->cache_count].order_id = oid;
                strncpy(sys->cache[sys->cache_count].cached_data, sys->outbox[i].payload, 127);
                sys->cache[sys->cache_count].version = ver;
                sys->cache_count++;
            }

            sys->outbox[i].processed = true;
        }
    }
}

// Швидке читання з L1 Кешу
const char* read_order_fast(polyglot_system_t *sys, int order_id) {
    for (size_t i = 0; i < sys->cache_count; ++i) {
        if (sys->cache[i].order_id == order_id) {
            return sys->cache[i].cached_data;
        }
    }
    return NULL; // Кеш-промах, читання з основної БД
}

int main(void) {
    polyglot_system_t system;
    polyglot_init(&system);

    // 1. Створення замовлення в основній БД
    create_order_transaction(&system, 1001, "Dmytro", 450.0);
    printf("Order 1001 created in Primary OLTP.\n");

    // Читання з кешу до синхронізації
    const char *cached = read_order_fast(&system, 1001);
    printf("Cache state before sync: %s\n", cached ? cached : "CACHE_MISS");

    // 2. Фоновий процес CDC / Outbox
    process_outbox_events(&system);

    // Читання з кешу після синхронізації
    cached = read_order_fast(&system, 1001);
    printf("Cache state after sync: %s\n", cached ? cached : "CACHE_MISS");

    return 0;
}
