#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define TABLE_SIZE_POWER_OF_TWO 16 // 2^4 = 16 слотів

typedef struct {
    uint64_t key;
    uint32_t value;
    bool occupied;
} HashEntry;

typedef struct {
    HashEntry entries[TABLE_SIZE_POWER_OF_TWO];
} TriangularHashTable;

static inline uint32_t hash_function(uint64_t key) {
    /* Проста хеш-функція Мура для 64-бітних цілих */
    key = (key ^ (key >> 30)) * 0xbf58476d1ce4e5b9ULL;
    key = (key ^ (key >> 27)) * 0x94d049bb133111ebULL;
    key = key ^ (key >> 31);
    return (uint32_t)key;
}

bool hash_table_insert(TriangularHashTable *table, uint64_t key, uint32_t val) {
    uint32_t h = hash_function(key);
    
    for (uint32_t step = 0; step < TABLE_SIZE_POWER_OF_TWO; step++) {
        /* Обчислимо step-не трикутне число T[step] */
        uint32_t tri_offset = step * (step + 1) / 2;
        uint32_t slot = (h + tri_offset) & (TABLE_SIZE_POWER_OF_TWO - 1);
        
        if (!table->entries[slot].occupied || table->entries[slot].key == key) {
            table->entries[slot].key = key;
            table->entries[slot].value = val;
            table->entries[slot].occupied = true;
            return true;
        }
    }
    
    return false; // Таблиця повністю заповнена
}
