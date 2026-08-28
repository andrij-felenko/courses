#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_ENTRIES 1024
#define MAX_KEY_LEN 64
#define MAX_VAL_LEN 256
#define DB_FILENAME "mini_kv_data.db"

#pragma pack(push, 1)
typedef struct {
    uint64_t timestamp;
    uint16_t key_len;
    uint32_t val_len;
} record_header_t;
#pragma pack(pop)

typedef struct {
    char key[MAX_KEY_LEN];
    long file_offset;
    uint32_t val_len;
} keydir_entry_t;

typedef struct {
    keydir_entry_t entries[MAX_ENTRIES];
    size_t count;
    FILE *db_file;
} kv_store_t;

int kv_init(kv_store_t *store) {
    store->count = 0;
    store->db_file = fopen(DB_FILENAME, "a+b");
    if (!store->db_file) return -1;
    return 0;
}

int kv_set(kv_store_t *store, const char *key, const char *value) {
    uint16_t klen = (uint16_t)strlen(key);
    uint32_t vlen = (uint32_t)strlen(value);

    fseek(store->db_file, 0, SEEK_END);
    long record_offset = ftell(store->db_file);

    record_header_t hdr;
    hdr.timestamp = (uint64_t)time(NULL);
    hdr.key_len = klen;
    hdr.val_len = vlen;

    // 1. Послідовний запис у журнал (Append-Only)
    fwrite(&hdr, sizeof(record_header_t), 1, store->db_file);
    fwrite(key, 1, klen, store->db_file);
    fwrite(value, 1, vlen, store->db_file);
    fflush(store->db_file);

    // 2. Оновлення індексу в пам'яті (KeyDir)
    long val_offset = record_offset + sizeof(record_header_t) + klen;

    for (size_t i = 0; i < store->count; ++i) {
        if (strcmp(store->entries[i].key, key) == 0) {
            store->entries[i].file_offset = val_offset;
            store->entries[i].val_len = vlen;
            return 0;
        }
    }

    if (store->count < MAX_ENTRIES) {
        strncpy(store->entries[store->count].key, key, MAX_KEY_LEN - 1);
        store->entries[store->count].file_offset = val_offset;
        store->entries[store->count].val_len = vlen;
        store->count++;
    }

    return 0;
}

int kv_get(kv_store_t *store, const char *key, char *out_val, size_t max_out) {
    for (size_t i = 0; i < store->count; ++i) {
        if (strcmp(store->entries[i].key, key) == 0) {
            long offset = store->entries[i].file_offset;
            uint32_t vlen = store->entries[i].val_len;

            if (vlen >= max_out) return -2; // Буфер замалий

            fseek(store->db_file, offset, SEEK_SET);
            fread(out_val, 1, vlen, store->db_file);
            out_val[vlen] = '\0';
            return 0;
        }
    }
    return -1; // Ключ не знайдено
}

int kv_delete(kv_store_t *store, const char *key) {
    // Запис маркеру видалення (Tombstone з довжиною значення 0)
    uint16_t klen = (uint16_t)strlen(key);
    record_header_t hdr;
    hdr.timestamp = (uint64_t)time(NULL);
    hdr.key_len = klen;
    hdr.val_len = 0; // Маркер Tombstone

    fseek(store->db_file, 0, SEEK_END);
    fwrite(&hdr, sizeof(record_header_t), 1, store->db_file);
    fwrite(key, 1, klen, store->db_file);
    fflush(store->db_file);

    // Видалення з індексу KeyDir
    for (size_t i = 0; i < store->count; ++i) {
        if (strcmp(store->entries[i].key, key) == 0) {
            store->entries[i] = store->entries[store->count - 1];
            store->count--;
            return 0;
        }
    }
    return -1;
}

void kv_close(kv_store_t *store) {
    if (store->db_file) {
        fclose(store->db_file);
        store->db_file = NULL;
    }
}
