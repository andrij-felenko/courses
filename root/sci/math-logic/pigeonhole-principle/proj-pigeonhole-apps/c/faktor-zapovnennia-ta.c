#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int key;
    int value;
    int occupied;
} HashEntry;

typedef struct {
    HashEntry* entries;
    size_t capacity;
    size_t count;
} HashTable;

HashTable* hashtable_create(size_t capacity) {
    HashTable* table = (HashTable*)malloc(sizeof(HashTable));
    if (!table) return NULL;

    table->entries = (HashEntry*)calloc(capacity, sizeof(HashEntry));
    table->capacity = capacity;
    table->count = 0;
    return table;
}

void hashtable_free(HashTable* table) {
    if (table) {
        free(table->entries);
        free(table);
    }
}

int hashtable_insert(HashTable* table, int key, int value, size_t* probe_collisions) {
    if (!table || table->count >= table->capacity) {
        // Межа Діріхле: n = capacity + 1 об'єктів не можна вставити в capacity комірок!
        return 0; 
    }

    size_t hash = (size_t)((unsigned int)key % table->capacity);
    size_t idx = hash;
    size_t collisions = 0;

    while (table->entries[idx].occupied) {
        if (table->entries[idx].key == key) {
            table->entries[idx].value = value; // Оновлення значення
            if (probe_collisions) *probe_collisions = collisions;
            return 1;
        }
        collisions++;
        idx = (idx + 1) % table->capacity;
    }

    table->entries[idx].key = key;
    table->entries[idx].value = value;
    table->entries[idx].occupied = 1;
    table->count++;

    if (probe_collisions) *probe_collisions = collisions;
    return 1;
}

int main(void) {
    size_t capacity = 5;
    HashTable* ht = hashtable_create(capacity);

    printf("=== Аналіз колізій у хеш-таблиці ємністю M = %zu ===\n", capacity);
    int keys[] = { 10, 15, 20, 25, 30, 35 };

    for (size_t i = 0; i < sizeof(keys)/sizeof(keys[0]); ++i) {
        size_t col = 0;
        int ok = hashtable_insert(ht, keys[i], (int)(i + 1) * 100, &col);
        if (ok) {
            printf("Ключ %2d вставлено (колізій зондування: %zu). Елементів у таблиці: %zu/%zu\n",
                   keys[i], col, ht->count, ht->capacity);
        } else {
            printf("Ключ %2d ВІДХИЛЕНО: Межа Діріхле! Таблиця повна (%zu/%zu)\n",
                   keys[i], ht->count, ht->capacity);
        }
    }

    hashtable_free(ht);
    return 0;
}
