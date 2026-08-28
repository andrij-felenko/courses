#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

/* Коди результатів трансляції */
typedef enum {
    TRANS_OK = 0,
    TRANS_ERR_SYNTAX = 1,
    TRANS_ERR_INVALID_CURRENCY = 2,
    TRANS_ERR_INVALID_STATUS = 3,
    TRANS_ERR_INVALID_AMOUNT = 4,
    TRANS_ERR_BUFFER_OVERFLOW = 5
} TranslateStatus;

/* Канонічні статуси замовлення */
typedef enum {
    CANONICAL_STATUS_CREATED = 1,
    CANONICAL_STATUS_CONFIRMED = 2,
    CANONICAL_STATUS_SHIPPED = 3,
    CANONICAL_STATUS_CANCELLED = 4
} CanonicalOrderStatus;

/* Канонічна модель даних замовлення */
typedef struct {
    char message_id[37];
    char correlation_id[64];
    uint64_t timestamp_ms;
    uint32_t schema_version;

    uint64_t order_id;
    char customer_ref[32];
    uint64_t amount_cents;
    char currency[4];
    CanonicalOrderStatus status;
} CanonicalOrderMessage;

/* Структура для мертвої черги (DLQ) */
typedef struct {
    char dlq_id[37];
    TranslateStatus error_code;
    char error_reason[128];
    uint64_t failed_at_ms;
    char raw_payload[512];
} DeadLetterEnvelope;

/* Допоміжні функції часу та генерації ID */
static uint64_t current_time_millis(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)(ts.tv_sec * 1000ULL + ts.tv_nsec / 1000000ULL);
}

static void generate_dummy_uuid(char *out, size_t size, uint64_t seed) {
    snprintf(out, size, "msg-%08lx-%04x-4000-8000-%012lx",
             (unsigned long)(seed & 0xFFFFFFFF),
             (unsigned int)((seed >> 32) & 0xFFFF),
             (unsigned long)(seed ^ 0xDEADBEEFULL));
}

/* 1. Синтаксичний парсинг і семантична валідація вхідного тексту */
TranslateStatus translate_legacy_message(
    const char *raw_input,
    const char *correlation_id,
    CanonicalOrderMessage *out_msg,
    DeadLetterEnvelope *out_dlq
) {
    if (!raw_input || !out_msg || !out_dlq) {
        return TRANS_ERR_SYNTAX;
    }

    uint64_t order_id = 0;
    char cust[32] = {0};
    uint64_t cents = 0;
    char curr[8] = {0};
    int raw_status = 0;

    /* Очікуваний формат рядка: order_id;cust_ref;amount_cents;currency;status_code */
    int parsed = sscanf(raw_input, "%lu;%31[^;];%lu;%7[^;];%d",
                        &order_id, cust, &cents, curr, &raw_status);

    if (parsed != 5) {
        out_dlq->error_code = TRANS_ERR_SYNTAX;
        snprintf(out_dlq->error_reason, sizeof(out_dlq->error_reason),
                 "Invalid syntax: expected 5 fields separated by semicolon, parsed %d", parsed);
        out_dlq->failed_at_ms = current_time_millis();
        generate_dummy_uuid(out_dlq->dlq_id, sizeof(out_dlq->dlq_id), out_dlq->failed_at_ms);
        snprintf(out_dlq->raw_payload, sizeof(out_dlq->raw_payload), "%s", raw_input);
        return TRANS_ERR_SYNTAX;
    }

    /* Семантична перевірка суми */
    if (cents == 0 || cents > 100000000000ULL) {
        out_dlq->error_code = TRANS_ERR_INVALID_AMOUNT;
        snprintf(out_dlq->error_reason, sizeof(out_dlq->error_reason),
                 "Invalid amount_cents: %lu out of allowed range (1..100000000000)", cents);
        out_dlq->failed_at_ms = current_time_millis();
        generate_dummy_uuid(out_dlq->dlq_id, sizeof(out_dlq->dlq_id), out_dlq->failed_at_ms);
        snprintf(out_dlq->raw_payload, sizeof(out_dlq->raw_payload), "%s", raw_input);
        return TRANS_ERR_INVALID_AMOUNT;
    }

    /* Семантична перевірка валюти */
    if (strcmp(curr, "UAH") != 0 && strcmp(curr, "USD") != 0 && strcmp(curr, "EUR") != 0) {
        out_dlq->error_code = TRANS_ERR_INVALID_CURRENCY;
        snprintf(out_dlq->error_reason, sizeof(out_dlq->error_reason),
                 "Unsupported currency code: '%s'", curr);
        out_dlq->failed_at_ms = current_time_millis();
        generate_dummy_uuid(out_dlq->dlq_id, sizeof(out_dlq->dlq_id), out_dlq->failed_at_ms);
        snprintf(out_dlq->raw_payload, sizeof(out_dlq->raw_payload), "%s", raw_input);
        return TRANS_ERR_INVALID_CURRENCY;
    }

    /* Мапінг застарілих статусів на канонічні */
    CanonicalOrderStatus canonical_status;
    switch (raw_status) {
        case 101: canonical_status = CANONICAL_STATUS_CREATED; break;
        case 102: canonical_status = CANONICAL_STATUS_CONFIRMED; break;
        case 103: canonical_status = CANONICAL_STATUS_SHIPPED; break;
        case 999: canonical_status = CANONICAL_STATUS_CANCELLED; break;
        default:
            out_dlq->error_code = TRANS_ERR_INVALID_STATUS;
            snprintf(out_dlq->error_reason, sizeof(out_dlq->error_reason),
                     "Unknown legacy status code: %d", raw_status);
            out_dlq->failed_at_ms = current_time_millis();
            generate_dummy_uuid(out_dlq->dlq_id, sizeof(out_dlq->dlq_id), out_dlq->failed_at_ms);
            snprintf(out_dlq->raw_payload, sizeof(out_dlq->raw_payload), "%s", raw_input);
            return TRANS_ERR_INVALID_STATUS;
    }

    /* Заповнення канонічного повідомлення */
    out_msg->timestamp_ms = current_time_millis();
    out_msg->schema_version = 1;
    generate_dummy_uuid(out_msg->message_id, sizeof(out_msg->message_id), out_msg->timestamp_ms);
    snprintf(out_msg->correlation_id, sizeof(out_msg->correlation_id), "%s",
             correlation_id ? correlation_id : "unknown-trace");

    out_msg->order_id = order_id;
    snprintf(out_msg->customer_ref, sizeof(out_msg->customer_ref), "%s", cust);
    out_msg->amount_cents = cents;
    snprintf(out_msg->currency, sizeof(out_msg->currency), "%s", curr);
    out_msg->status = canonical_status;

    return TRANS_OK;
}

/* 2. Бінарна серіалізація канонічного повідомлення */
size_t serialize_canonical_message(
    const CanonicalOrderMessage *msg,
    uint8_t *out_buf,
    size_t buf_size
) {
    if (!msg || !out_buf || buf_size < 256) {
        return 0;
    }

    /* Простий двійковий формат: заголовок + фіксовані поля + строки */
    size_t offset = 0;

    /* Магічний байт формату 0xCF 0x01 (Canonical Format v1) */
    out_buf[offset++] = 0xCF;
    out_buf[offset++] = 0x01;

    /* Запис schema_version (4 байти, little-endian) */
    uint32_t ver = msg->schema_version;
    memcpy(out_buf + offset, &ver, sizeof(ver));
    offset += sizeof(ver);

    /* Запис timestamp_ms (8 байтів) */
    uint64_t ts = msg->timestamp_ms;
    memcpy(out_buf + offset, &ts, sizeof(ts));
    offset += sizeof(ts);

    /* Запис order_id (8 байтів) */
    uint64_t oid = msg->order_id;
    memcpy(out_buf + offset, &oid, sizeof(oid));
    offset += sizeof(oid);

    /* Запис amount_cents (8 байтів) */
    uint64_t amt = msg->amount_cents;
    memcpy(out_buf + offset, &amt, sizeof(amt));
    offset += sizeof(amt);

    /* Запис статусу (1 байт) */
    out_buf[offset++] = (uint8_t)msg->status;

    /* Запис валюти (4 байти фіксовано) */
    memcpy(out_buf + offset, msg->currency, 4);
    offset += 4;

    /* Запис довжини та тіла customer_ref */
    uint8_t cust_len = (uint8_t)strlen(msg->customer_ref);
    out_buf[offset++] = cust_len;
    memcpy(out_buf + offset, msg->customer_ref, cust_len);
    offset += cust_len;

    return offset;
}
