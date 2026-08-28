#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define WIRE_MAGIC_BYTE 0x00
#define WIRE_HEADER_SIZE 5
#define CACHE_CAPACITY 256

/* Елемент фіксованої таблиці локального кешу */
typedef struct {
    uint32_t schema_id;
    char *schema_json;
    bool is_active;
} SchemaCacheEntry;

typedef struct {
    SchemaCacheEntry entries[CACHE_CAPACITY];
    size_t count;
} LocalSchemaCache;

void cache_init(LocalSchemaCache *cache) {
    memset(cache, 0, sizeof(LocalSchemaCache));
}

void cache_free(LocalSchemaCache *cache) {
    for (size_t i = 0; i < CACHE_CAPACITY; ++i) {
        if (cache->entries[i].is_active && cache->entries[i].schema_json) {
            free(cache->entries[i].schema_json);
            cache->entries[i].schema_json = NULL;
            cache->entries[i].is_active = false;
        }
    }
    cache->count = 0;
}

bool cache_put(LocalSchemaCache *cache, uint32_t id, const char *json) {
    size_t slot = id % CACHE_CAPACITY;
    if (cache->entries[slot].is_active) {
        free(cache->entries[slot].schema_json);
    } else {
        cache->count++;
    }
    cache->entries[slot].schema_id = id;
    cache->entries[slot].schema_json = strdup(json);
    cache->entries[slot].is_active = true;
    return cache->entries[slot].schema_json != NULL;
}

const char* cache_get(const LocalSchemaCache *cache, uint32_t id) {
    size_t slot = id % CACHE_CAPACITY;
    if (cache->entries[slot].is_active && cache->entries[slot].schema_id == id) {
        return cache->entries[slot].schema_json;
    }
    return NULL;
}

/* Кодування кадру Confluent Wire Format (1 магічний байт + 4 байти Big-Endian ID) */
uint8_t* wire_encode(uint32_t schema_id, const uint8_t *payload, size_t payload_len, size_t *out_len) {
    *out_len = WIRE_HEADER_SIZE + payload_len;
    uint8_t *buffer = (uint8_t*)malloc(*out_len);
    if (!buffer) return NULL;

    /* Байт 0: Magic byte */
    buffer[0] = WIRE_MAGIC_BYTE;

    /* Байти 1–4: 32-бітний Schema ID у мережевому порядку (Big-Endian) */
    buffer[1] = (uint8_t)((schema_id >> 24) & 0xFF);
    buffer[2] = (uint8_t)((schema_id >> 16) & 0xFF);
    buffer[3] = (uint8_t)((schema_id >> 8) & 0xFF);
    buffer[4] = (uint8_t)(schema_id & 0xFF);

    /* Байти 5...N: Бінарне тіло */
    memcpy(buffer + WIRE_HEADER_SIZE, payload, payload_len);
    return buffer;
}

/* Декодування та валідація кадру */
bool wire_decode(const uint8_t *buffer, size_t buffer_len, uint32_t *out_schema_id, const uint8_t **out_payload, size_t *out_payload_len) {
    if (buffer_len < WIRE_HEADER_SIZE) {
        return false;
    }
    if (buffer[0] != WIRE_MAGIC_BYTE) {
        return false; /* Невідомий магічний байт: повідомлення пошкоджене або не є Wire Format */
    }

    *out_schema_id = ((uint32_t)buffer[1] << 24) |
                     ((uint32_t)buffer[2] << 16) |
                     ((uint32_t)buffer[3] << 8)  |
                     ((uint32_t)buffer[4]);

    *out_payload = buffer + WIRE_HEADER_SIZE;
    *out_payload_len = buffer_len - WIRE_HEADER_SIZE;
    return true;
}
