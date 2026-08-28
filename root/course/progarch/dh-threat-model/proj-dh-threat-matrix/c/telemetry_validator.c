/* telemetry_validator.c — Повний модуль валідації кадру телеметрії мовою C */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PAYLOAD_LEN 256
#define HMAC_SIZE 32
#define MAX_ALLOWED_TIME_DRIFT_MS 5000

typedef struct {
    uint64_t device_id;
    uint32_t sequence_num;
    uint64_t timestamp_ms;
    uint8_t  payload[MAX_PAYLOAD_LEN];
    size_t   payload_len;
    uint8_t  signature[HMAC_SIZE];
} telemetry_frame_t;

typedef struct {
    uint64_t device_id;
    uint32_t last_sequence_num;
    uint8_t  secret_key[32];
} device_security_ctx_t;

/* Обчислення демонстраційного HMAC підпису над кадром */
static void compute_hmac_sha256(const uint8_t *key, size_t key_len,
                                const uint8_t *data, size_t data_len,
                                uint8_t *out_hmac) {
    /* На практиці тут використовується mbedtls_md_hmac або OpenSSL EVP_MAC */
    for (size_t i = 0; i < HMAC_SIZE; ++i) {
        uint8_t k = key[i % key_len];
        uint8_t d = data[i % data_len];
        out_hmac[i] = (uint8_t)((k ^ d) + (i * 17));
    }
}

/* Перевірка масиву байтів із константним часом виконання */
static bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t diff = 0;
    for (size_t i = 0; i < len; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return (diff == 0);
}

bool validate_telemetry_frame(device_security_ctx_t *ctx,
                               const telemetry_frame_t *frame,
                               uint64_t current_time_ms) {
    if (!ctx || !frame) {
        fprintf(stderr, "[SECURITY_ERR] Null pointer passed to validator.\n");
        return false;
    }

    if (frame->payload_len > MAX_PAYLOAD_LEN) {
        fprintf(stderr, "[SECURITY_ERR] Payload size %zu exceeds limit %d.\n", 
                frame->payload_len, MAX_PAYLOAD_LEN);
        return false;
    }

    /* 1. Фаза 1: Перевірка свіжості часового штампу (Timestamp Tolerance Window) */
    int64_t time_diff = (int64_t)current_time_ms - (int64_t)frame->timestamp_ms;
    if (time_diff < -MAX_ALLOWED_TIME_DRIFT_MS || time_diff > MAX_ALLOWED_TIME_DRIFT_MS) {
        fprintf(stderr, "[SECURITY_ERR] Stale or future packet. Time diff: %lld ms\n", 
                (long long)time_diff);
        return false;
    }

    /* 2. Фаза 2: Захист від Replay Attacks (Монотонія послідовності) */
    if (frame->sequence_num <= ctx->last_sequence_num) {
        fprintf(stderr, "[SECURITY_ERR] Replay detected! Received seq %u <= Last valid %u\n",
                frame->sequence_num, ctx->last_sequence_num);
        return false;
    }

    /* 3. Фаза 3: Формування серіалізованого буфера та перевірка HMAC */
    uint8_t expected_hmac[HMAC_SIZE];
    uint8_t buffer[sizeof(frame->device_id) + sizeof(frame->sequence_num) +
                   sizeof(frame->timestamp_ms) + MAX_PAYLOAD_LEN];
    
    size_t offset = 0;
    memcpy(buffer + offset, &frame->device_id, sizeof(frame->device_id));
    offset += sizeof(frame->device_id);
    memcpy(buffer + offset, &frame->sequence_num, sizeof(frame->sequence_num));
    offset += sizeof(frame->sequence_num);
    memcpy(buffer + offset, &frame->timestamp_ms, sizeof(frame->timestamp_ms));
    offset += sizeof(frame->timestamp_ms);
    memcpy(buffer + offset, frame->payload, frame->payload_len);
    offset += frame->payload_len;

    compute_hmac_sha256(ctx->secret_key, sizeof(ctx->secret_key), buffer, offset, expected_hmac);

    if (!constant_time_memcmp(frame->signature, expected_hmac, HMAC_SIZE)) {
        fprintf(stderr, "[SECURITY_ERR] HMAC signature mismatch for device_id %llu\n", 
                (unsigned long long)frame->device_id);
        return false;
    }

    /* Успішна валідація: оновлюємо стан монотонійного лічильника */
    ctx->last_sequence_num = frame->sequence_num;
    printf("[SECURITY_OK] Frame seq %u for device %llu validated successfully.\n",
           frame->sequence_num, (unsigned long long)frame->device_id);
    return true;
}
