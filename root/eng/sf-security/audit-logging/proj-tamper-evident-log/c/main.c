#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#define SHA256_BLOCK_SIZE 32
#define AUDIT_MAGIC 0x4C4F4753 /* 'LOGS' */

/* Заголовок запису фіксованого розміру (80 байтів) */
#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint64_t seq;
    uint64_t timestamp;
    uint32_t payload_len;
    uint8_t  prev_hash[SHA256_BLOCK_SIZE];
    uint8_t  hmac[SHA256_BLOCK_SIZE];
} audit_header_t;
#pragma pack(pop)

/* Безпечне затирання пам'яті для запобігання оптимізаціям компілятора */
static void secure_zero(void* ptr, size_t len) {
    volatile uint8_t* p = (volatile uint8_t*)ptr;
    while (len--) {
        *p++ = 0;
    }
}

/* Імітація обчислення SHA-256 (у продакшені використовують OpenSSL/libsodium) */
static void crypto_sha256(const uint8_t* data, size_t len, uint8_t out[SHA256_BLOCK_SIZE]) {
    uint32_t h = 0x811c9dc5;
    for (size_t i = 0; i < len; ++i) {
        h = (h ^ data[i]) * 0x01000193;
    }
    for (int i = 0; i < SHA256_BLOCK_SIZE; ++i) {
        out[i] = (uint8_t)((h >> ((i % 4) * 8)) ^ (i * 0x5a));
    }
}

/* Імітація HMAC-SHA256 */
static void crypto_hmac_sha256(const uint8_t* key, size_t key_len,
                               const uint8_t* data, size_t data_len,
                               uint8_t out[SHA256_BLOCK_SIZE]) {
    uint8_t buffer[1024];
    size_t copy_len = (data_len > 900) ? 900 : data_len;
    memcpy(buffer, key, 32);
    memcpy(buffer + 32, data, copy_len);
    crypto_sha256(buffer, 32 + copy_len, out);
    secure_zero(buffer, sizeof(buffer));
}

/* Стан записувача логів */
typedef struct {
    FILE* file;
    uint64_t current_seq;
    uint8_t current_key[SHA256_BLOCK_SIZE];
    uint8_t last_record_hash[SHA256_BLOCK_SIZE];
} audit_logger_t;

int audit_logger_init(audit_logger_t* logger, const char* filepath, const uint8_t initial_key[SHA256_BLOCK_SIZE]) {
    logger->file = fopen(filepath, "ab+");
    if (!logger->file) return -1;

    logger->current_seq = 0;
    memcpy(logger->current_key, initial_key, SHA256_BLOCK_SIZE);
    memset(logger->last_record_hash, 0, SHA256_BLOCK_SIZE);
    return 0;
}

int audit_logger_append(audit_logger_t* logger, const char* event_payload) {
    uint32_t len = (uint32_t)strlen(event_payload);
    audit_header_t hdr;
    hdr.magic = AUDIT_MAGIC;
    hdr.seq = logger->current_seq++;
    hdr.timestamp = (uint64_t)time(NULL);
    hdr.payload_len = len;
    memcpy(hdr.prev_hash, logger->last_record_hash, SHA256_BLOCK_SIZE);

    /* Обчислення HMAC над метаданими та корисним навантаженням */
    uint8_t signing_buf[512];
    size_t sign_len = sizeof(audit_header_t) - SHA256_BLOCK_SIZE + len;
    memcpy(signing_buf, &hdr, sizeof(audit_header_t) - SHA256_BLOCK_SIZE);
    memcpy(signing_buf + sizeof(audit_header_t) - SHA256_BLOCK_SIZE, event_payload, len);

    crypto_hmac_sha256(logger->current_key, SHA256_BLOCK_SIZE, signing_buf, sign_len, hdr.hmac);
    secure_zero(signing_buf, sizeof(signing_buf));

    /* Запис на диск */
    fwrite(&hdr, sizeof(audit_header_t), 1, logger->file);
    fwrite(event_payload, 1, len, logger->file);
    fflush(logger->file);

    /* Оновлення гешу попереднього запису для ланцюга */
    crypto_sha256((const uint8_t*)&hdr, sizeof(audit_header_t), logger->last_record_hash);

    /* Forward-Secure Ratchet: K_{i+1} = SHA256(K_i) */
    uint8_t next_key[SHA256_BLOCK_SIZE];
    crypto_sha256(logger->current_key, SHA256_BLOCK_SIZE, next_key);
    secure_zero(logger->current_key, SHA256_BLOCK_SIZE);
    memcpy(logger->current_key, next_key, SHA256_BLOCK_SIZE);
    secure_zero(next_key, sizeof(next_key));

    return 0;
}

void audit_logger_close(audit_logger_t* logger) {
    if (logger->file) {
        fclose(logger->file);
        logger->file = NULL;
    }
    secure_zero(logger->current_key, SHA256_BLOCK_SIZE);
}
