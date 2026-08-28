#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ITEMS 128
#define KEY_MAX_LEN 64
#define VAL_MAX_LEN 256

typedef struct {
    char pk[KEY_MAX_LEN];
    char sk[KEY_MAX_LEN];
    char gsi1pk[KEY_MAX_LEN];
    char gsi1sk[KEY_MAX_LEN];
    char entity_type[32];
    char payload[VAL_MAX_LEN];
} single_table_item_t;

typedef struct {
    single_table_item_t items[MAX_ITEMS];
    size_t count;
} single_table_t;

void table_init(single_table_t *t) {
    t->count = 0;
}

int table_put(single_table_t *t, const char *pk, const char *sk, 
              const char *gsi1pk, const char *gsi1sk,
              const char *type, const char *payload) {
    // Перевірка на оновлення існуючого ключа
    for (size_t i = 0; i < t->count; ++i) {
        if (strcmp(t->items[i].pk, pk) == 0 && strcmp(t->items[i].sk, sk) == 0) {
            strncpy(t->items[i].payload, payload, VAL_MAX_LEN - 1);
            strncpy(t->items[i].entity_type, type, 31);
            if (gsi1pk) strncpy(t->items[i].gsi1pk, gsi1pk, KEY_MAX_LEN - 1);
            if (gsi1sk) strncpy(t->items[i].gsi1sk, gsi1sk, KEY_MAX_LEN - 1);
            return 0;
        }
    }

    if (t->count >= MAX_ITEMS) return -1;

    single_table_item_t *item = &t->items[t->count++];
    strncpy(item->pk, pk, KEY_MAX_LEN - 1);
    strncpy(item->sk, sk, KEY_MAX_LEN - 1);
    strncpy(item->gsi1pk, gsi1pk ? gsi1pk : "", KEY_MAX_LEN - 1);
    strncpy(item->gsi1sk, gsi1sk ? gsi1sk : "", KEY_MAX_LEN - 1);
    strncpy(item->entity_type, type, 31);
    strncpy(item->payload, payload, VAL_MAX_LEN - 1);

    return 0;
}

// Запит GetItem за точним збігом PK та SK
const single_table_item_t* table_get_item(const single_table_t *t, const char *pk, const char *sk) {
    for (size_t i = 0; i < t->count; ++i) {
        if (strcmp(t->items[i].pk, pk) == 0 && strcmp(t->items[i].sk, sk) == 0) {
            return &t->items[i];
        }
    }
    return NULL;
}

// Запит Query за PK та префіксом Sort Key (begins_with)
size_t table_query(const single_table_t *t, const char *pk, const char *sk_prefix, 
                   const single_table_item_t *out_items[], size_t max_results) {
    size_t found = 0;
    size_t prefix_len = sk_prefix ? strlen(sk_prefix) : 0;

    for (size_t i = 0; i < t->count && found < max_results; ++i) {
        if (strcmp(t->items[i].pk, pk) == 0) {
            if (prefix_len == 0 || strncmp(t->items[i].sk, sk_prefix, prefix_len) == 0) {
                out_items[found++] = &t->items[i];
            }
        }
    }
    return found;
}

// Запит через GSI1
size_t table_query_gsi1(const single_table_t *t, const char *gsi1pk,
                        const single_table_item_t *out_items[], size_t max_results) {
    size_t found = 0;
    for (size_t i = 0; i < t->count && found < max_results; ++i) {
        if (strcmp(t->items[i].gsi1pk, gsi1pk) == 0) {
            out_items[found++] = &t->items[i];
        }
    }
    return found;
}

// Функція видалення сутності
int table_delete(single_table_t *t, const char *pk, const char *sk) {
    for (size_t i = 0; i < t->count; ++i) {
        if (strcmp(t->items[i].pk, pk) == 0 && strcmp(t->items[i].sk, sk) == 0) {
            t->items[i] = t->items[t->count - 1];
            t->count--;
            return 0;
        }
    }
    return -1;
}

int main(void) {
    single_table_t db;
    table_init(&db);

    // Додавання даних користувача, замовлення та адреси
    table_put(&db, "USER#1001", "#METADATA", NULL, NULL, "User", "{\"name\": \"Alex\"}");
    table_put(&db, "USER#1001", "ORDER#2024-05-12#001", "ORDER#001", "USER#1001", "Order", "{\"total\": 120.5}");
    table_put(&db, "USER#1001", "ADDR#HOME", NULL, NULL, "Address", "{\"city\": \"Kyiv\"}");

    // 1. Вибірка всіх даних користувача за 1 запит
    const single_table_item_t *results[10];
    size_t count = table_query(&db, "USER#1001", NULL, results, 10);
    printf("User collection items: %zu\n", count);

    // 2. Зворотний пошук замовлення через GSI
    size_t gsi_count = table_query_gsi1(&db, "ORDER#001", results, 10);
    if (gsi_count > 0) {
        printf("Found order owner: %s\n", results[0]->pk);
    }

    return 0;
}
