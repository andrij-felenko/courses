/* C: Реалізація Edge Filter (in-memory hash table з TTL)
   та Domain Transactional Check */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>

#define TABLE_SIZE 1024
#define DEFAULT_TTL_SECONDS 300

typedef struct CacheEntry {
    char key[64];
    time_t expires_at;
    struct CacheEntry* next;
} CacheEntry;

typedef struct {
    CacheEntry* buckets[TABLE_SIZE];
} EdgeDeduplicator;

/* Проста хеш-функція djb2 */
static unsigned long hash_key(const char* str) {
    unsigned long hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % TABLE_SIZE;
}

EdgeDeduplicator* edge_dedup_create(void) {
    EdgeDeduplicator* dedup = (EdgeDeduplicator*)calloc(1, sizeof(EdgeDeduplicator));
    return dedup;
}

void edge_dedup_destroy(EdgeDeduplicator* dedup) {
    if (!dedup) return;
    for (int i = 0; i < TABLE_SIZE; i++) {
        CacheEntry* entry = dedup->buckets[i];
        while (entry) {
            CacheEntry* tmp = entry;
            entry = entry->next;
            free(tmp);
        }
    }
    free(dedup);
}

/* 1. Дедуплікація на межі (Edge Deduplication Check) */
bool edge_dedup_check_and_register(EdgeDeduplicator* dedup, const char* key, int ttl_seconds) {
    time_t now = time(NULL);
    unsigned long idx = hash_key(key);
    CacheEntry* entry = dedup->buckets[idx];

    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            if (entry->expires_at > now) {
                /* Знайдено активний дублікат на межі! */
                return false; 
            } else {
                /* Ключ застарів — оновлюємо TTL */
                entry->expires_at = now + ttl_seconds;
                return true;
            }
        }
        entry = entry->next;
    }

    /* Новий ключ — додаємо в кеш межі */
    CacheEntry* new_entry = (CacheEntry*)malloc(sizeof(CacheEntry));
    strncpy(new_entry->key, key, sizeof(new_entry->key) - 1);
    new_entry->key[sizeof(new_entry->key) - 1] = '\0';
    new_entry->expires_at = now + ttl_seconds;
    new_entry->next = dedup->buckets[idx];
    dedup->buckets[idx] = new_entry;

    return true; /* Запит унікальний для вікна межі */
}

/* 2. Дедуплікація у логіці / DB (Domain Transactional Check) */
typedef struct {
    bool is_duplicate_in_db;
} MockDatabaseTransaction;

bool domain_process_order_transactional(MockDatabaseTransaction* tx, const char* order_id, const char* key) {
    /* Симуляція виконання в межах BEGIN ... COMMIT */
    if (tx->is_duplicate_in_db) {
        /* UNIQUE constraint rollback у DB */
        printf("[Domain DB] UNIQUE constraint violation for key: %s. Rolling back!\n", key);
        return false;
    }

    /* Атомарний запис у БД: INSERT INTO orders + INSERT INTO processed_keys */
    printf("[Domain DB] Successfully inserted order %s with idempotency key %s (COMMITTED)\n", order_id, key);
    return true;
}

int main(void) {
    EdgeDeduplicator* edge = edge_dedup_create();
    const char* req_key = "REQ-PAYMENT-99812";

    printf("--- Траєкторія 1: Перший запит ---\n");
    if (edge_dedup_check_and_register(edge, req_key, DEFAULT_TTL_SECONDS)) {
        printf("[Edge Gateway] Key %s passed filter.\n", req_key);
        MockDatabaseTransaction tx1 = { .is_duplicate_in_db = false };
        domain_process_order_transactional(&tx1, "ORD-101", req_key);
    }

    printf("\n--- Траєкторія 2: Швидкий повтор (Retry) через 500мс ---\n");
    if (!edge_dedup_check_and_register(edge, req_key, DEFAULT_TTL_SECONDS)) {
        printf("[Edge Gateway] BLOCKED DUPLICATE key %s at boundary! DB not touched.\n", req_key);
    }

    edge_dedup_destroy(edge);
    return 0;
}
