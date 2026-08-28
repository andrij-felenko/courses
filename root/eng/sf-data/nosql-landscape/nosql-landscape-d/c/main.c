#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define MAX_KV 64

typedef struct {
    char key[32];
    char value[64];
    bool is_active;
} kv_pair_t;

typedef struct {
    kv_pair_t data[MAX_KV];
    size_t count;
} simple_store_t;

void store_init(simple_store_t *s) {
    s->count = 0;
}

int store_put(simple_store_t *s, const char *key, const char *val) {
    for (size_t i = 0; i < s->count; ++i) {
        if (strcmp(s->data[i].key, key) == 0) {
            strncpy(s->data[i].value, val, 63);
            s->data[i].is_active = true;
            printf("[LOG] Оновлено ключ '%s' -> '%s'\n", key, val);
            return 0;
        }
    }
    if (s->count < MAX_KV) {
        strncpy(s->data[s->count].key, key, 31);
        strncpy(s->data[s->count].value, val, 63);
        s->data[s->count].is_active = true;
        s->count++;
        printf("[LOG] Записано новий ключ '%s' -> '%s'\n", key, val);
        return 0;
    }
    return -1;
}

const char* store_get(const simple_store_t *s, const char *key) {
    for (size_t i = 0; i < s->count; ++i) {
        if (s->data[i].is_active && strcmp(s->data[i].key, key) == 0) {
            return s->data[i].value;
        }
    }
    return NULL; // Ключ не знайдено
}
