#include <stdio.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    int id;
    char payload[128];
} db_row_t;

typedef struct {
    int id;
    char cached_val[128];
} cache_row_t;

// Імітація атомарної транзакції
bool save_with_outbox(db_row_t *db, size_t *db_sz, int id, const char *data) {
    db[*db_sz].id = id;
    strncpy(db[*db_sz].payload, data, 127);
    (*db_sz)++;
    return true;
}

// Фонова синхронізація кешу
void sync_cache(const db_row_t *db, size_t db_sz, cache_row_t *cache, size_t *c_sz) {
    for (size_t i = 0; i < db_sz; ++i) {
        cache[i].id = db[i].id;
        strncpy(cache[i].cached_val, db[i].payload, 127);
    }
    *c_sz = db_sz;
}
