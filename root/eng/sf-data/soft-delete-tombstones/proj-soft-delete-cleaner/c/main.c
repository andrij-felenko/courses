#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BATCH_SIZE 3
#define GC_GRACE_SECONDS 864000 // 10 днів у секундах

typedef enum {
    ENTRY_DATA,
    ENTRY_TOMBSTONE
} EntryType;

typedef struct {
    int64_t id;
    int64_t timestamp;
    EntryType type;
    char key[32];
    char value[64];
} StorageRecord;

typedef struct {
    StorageRecord *records;
    size_t count;
    size_t capacity;
} StorageTable;

// Ініціалізація пам'яті для сховища
StorageTable* create_table(size_t capacity) {
    StorageTable *table = (StorageTable*)malloc(sizeof(StorageTable));
    table->records = (StorageRecord*)malloc(sizeof(StorageRecord) * capacity);
    table->count = 0;
    table->capacity = capacity;
    return table;
}

void free_table(StorageTable *table) {
    if (table) {
        free(table->records);
        free(table);
    }
}

void append_record(StorageTable *t, int64_t id, const char *key, const char *val, int64_t ts, EntryType type) {
    if (t->count >= t->capacity) return;
    StorageRecord *r = &t->records[t->count++];
    r->id = id;
    r->timestamp = ts;
    r->type = type;
    strncpy(r->key, key, sizeof(r->key) - 1);
    r->key[sizeof(r->key) - 1] = '\0';
    strncpy(r->value, val, sizeof(r->value) - 1);
    r->value[sizeof(r->value) - 1] = '\0';
}

// 1. Алгоритм неблокувального порційного видалення (Keyset Batch Purge)
size_t purge_soft_deleted_batch(StorageTable *table, int64_t cutoff_ts, int64_t *cursor_id, size_t limit) {
    size_t purged_in_batch = 0;
    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < table->count) {
        StorageRecord *r = &table->records[read_idx];

        // Якщо запис знаходиться після нашого курсора, є м'яко видаленим і старішим за cutoff
        if (r->id > *cursor_id && r->type == ENTRY_TOMBSTONE && r->timestamp < cutoff_ts && purged_in_batch < limit) {
            *cursor_id = r->id;
            purged_in_batch++;
            read_idx++; // Пропускаємо запис (фізично вивільняємо зі сховища)
        } else {
            if (write_idx != read_idx) {
                table->records[write_idx] = table->records[read_idx];
            }
            write_idx++;
            read_idx++;
        }
    }
    table->count = write_idx;
    return purged_in_batch;
}

// 2. Алгоритм злиття надгробків LSM (LSM Tombstone Compactor)
StorageTable* compact_lsm_levels(const StorageTable *level_new, const StorageTable *level_old, int64_t current_ts) {
    StorageTable *merged = create_table(level_new->count + level_old->count);
    size_t i = 0, j = 0;

    while (i < level_new->count || j < level_old->count) {
        if (i < level_new->count && j < level_old->count) {
            int cmp = strcmp(level_new->records[i].key, level_old->records[j].key);

            if (cmp == 0) {
                // Конфлікт ключів: новіший рівень перемагає старий
                if (level_new->records[i].type == ENTRY_TOMBSTONE) {
                    // Якщо це надгробок, але він ще захищений (< GC_GRACE), ми повинні його зберегти
                    if (current_ts - level_new->records[i].timestamp < GC_GRACE_SECONDS) {
                        append_record(merged, level_new->records[i].id, level_new->records[i].key,
                                      "", level_new->records[i].timestamp, ENTRY_TOMBSTONE);
                    }
                    // Якщо старіший за GC_GRACE — надгробок і старі дані повністю знищуються
                } else {
                    append_record(merged, level_new->records[i].id, level_new->records[i].key,
                                  level_new->records[i].value, level_new->records[i].timestamp, ENTRY_DATA);
                }
                i++;
                j++; // Старий запис відкинуто
            } else if (cmp < 0) {
                append_record(merged, level_new->records[i].id, level_new->records[i].key,
                              level_new->records[i].value, level_new->records[i].timestamp, level_new->records[i].type);
                i++;
            } else {
                append_record(merged, level_old->records[j].id, level_old->records[j].key,
                              level_old->records[j].value, level_old->records[j].timestamp, level_old->records[j].type);
                j++;
            }
        } else if (i < level_new->count) {
            append_record(merged, level_new->records[i].id, level_new->records[i].key,
                          level_new->records[i].value, level_new->records[i].timestamp, level_new->records[i].type);
            i++;
        } else {
            append_record(merged, level_old->records[j].id, level_old->records[j].key,
                          level_old->records[j].value, level_old->records[j].timestamp, level_old->records[j].type);
            j++;
        }
    }
    return merged;
}

int main(void) {
    StorageTable *db = create_table(10);
    append_record(db, 1, "user:1", "Alice", 100, ENTRY_DATA);
    append_record(db, 2, "user:2", "Bob", 200, ENTRY_TOMBSTONE); // М'яко видалений
    append_record(db, 3, "user:3", "Charlie", 300, ENTRY_DATA);
    append_record(db, 4, "user:4", "David", 250, ENTRY_TOMBSTONE); // М'яко видалений

    int64_t cursor = 0;
    int64_t cutoff = 500;
    size_t batch = 0;

    printf("Початок батчевого очищення сховища...\n");
    while (true) {
        size_t deleted = purge_soft_deleted_batch(db, cutoff, &cursor, 2);
        if (deleted == 0) break;
        batch++;
        printf("Батч #%zu: успішно видалено %zu записів. Курсор id=%lld\n", batch, deleted, (long long)cursor);
    }

    printf("Залишилося живих записів у таблиці: %zu\n", db->count);
    free_table(db);
    return 0;
}
