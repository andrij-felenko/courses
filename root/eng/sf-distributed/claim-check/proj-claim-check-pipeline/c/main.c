#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define THRESHOLD_BYTES (64 * 1024)
#define SHA256_HEX_LEN  65
#define MAX_URI_LEN     256

/* Проста реалізація хешування FNV-1a / SHA-імітатора для автономного прикладу */
static void compute_sha256_hex(const uint8_t *data, size_t len, char out_hex[SHA256_HEX_LEN]) {
    uint64_t h1 = 0xcbf29ce484222325ULL;
    uint64_t h2 = 0x100000001b3ULL;
    for (size_t i = 0; i < len; ++i) {
        h1 = (h1 ^ data[i]) * 0x100000001b3ULL;
        h2 = (h2 ^ (data[i] + i)) * 0xcbf29ce484222325ULL;
    }
    snprintf(out_hex, SHA256_HEX_LEN, "%016llx%016llx%016llx%016llx",
             (unsigned long long)h1, (unsigned long long)h2,
             (unsigned long long)(h1 ^ h2), (unsigned long long)(h1 + h2));
}

/* Структура дескриптора квитанції */
typedef struct {
    char claim_id[37];
    bool is_external;
    char storage_uri[MAX_URI_LEN];
    char content_sha256[SHA256_HEX_LEN];
    size_t size_bytes;
    uint8_t *inline_data;
} ClaimTicket;

/* Інтерфейс сховища блобів */
typedef struct {
    bool (*put_blob)(const char *key, const uint8_t *data, size_t size);
    bool (*get_blob)(const char *key, uint8_t **out_data, size_t *out_size);
} BlobStorageDriver;

/* Імітатор файлового / блокового сховища */
static bool mock_s3_put(const char *key, const uint8_t *data, size_t size) {
    printf("[Storage Driver] PUT '%s' (%zu байтів) -> HTTP 200 OK\n", key, size);
    return true;
}

static bool mock_s3_get(const char *key, uint8_t **out_data, size_t *out_size) {
    printf("[Storage Driver] GET '%s' -> HTTP 200 OK\n", key);
    *out_size = 120 * 1024;
    *out_data = (uint8_t *)malloc(*out_size);
    if (!*out_data) return false;
    memset(*out_data, 0xAB, *out_size);
    return true;
}

static BlobStorageDriver g_storage = { mock_s3_put, mock_s3_get };

/* Відправка з пороговою маршрутизацією */
bool claim_check_produce(const uint8_t *payload, size_t size, ClaimTicket *out_ticket) {
    if (!payload || !out_ticket) return false;
    memset(out_ticket, 0, sizeof(ClaimTicket));
    snprintf(out_ticket->claim_id, sizeof(out_ticket->claim_id), "clm-%08x", (unsigned int)size);
    out_ticket->size_bytes = size;

    if (size <= THRESHOLD_BYTES) {
        out_ticket->is_external = false;
        out_ticket->inline_data = (uint8_t *)malloc(size);
        if (!out_ticket->inline_data) return false;
        memcpy(out_ticket->inline_data, payload, size);
        compute_sha256_hex(payload, size, out_ticket->content_sha256);
        return true;
    }

    out_ticket->is_external = true;
    compute_sha256_hex(payload, size, out_ticket->content_sha256);
    snprintf(out_ticket->storage_uri, sizeof(out_ticket->storage_uri),
             "s3://corporate-events/blobs/%s", out_ticket->content_sha256);

    /* Синхронний запис у сховище до публікації квитанції */
    if (!g_storage.put_blob(out_ticket->storage_uri, payload, size)) {
        return false;
    }
    return true;
}

/* Отримання та верифікація цілісності споживачем */
bool claim_check_consume(const ClaimTicket *ticket, uint8_t **out_payload, size_t *out_size) {
    if (!ticket || !out_payload || !out_size) return false;

    if (!ticket->is_external) {
        *out_payload = (uint8_t *)malloc(ticket->size_bytes);
        if (!*out_payload) return false;
        memcpy(*out_payload, ticket->inline_data, ticket->size_bytes);
        *out_size = ticket->size_bytes;
        return true;
    }

    uint8_t *fetched_data = NULL;
    size_t fetched_size = 0;
    if (!g_storage.get_blob(ticket->storage_uri, &fetched_data, &fetched_size)) {
        return false;
    }

    /* Наскрізна верифікація SHA-256 */
    char verify_hex[SHA256_HEX_LEN];
    compute_sha256_hex(fetched_data, fetched_size, verify_hex);
    if (strncmp(verify_hex, ticket->content_sha256, SHA256_HEX_LEN) != 0) {
        printf("[Consumer Error] Невідповідність контрольної суми SHA-256!\n");
        free(fetched_data);
        return false;
    }

    *out_payload = fetched_data;
    *out_size = fetched_size;
    return true;
}
