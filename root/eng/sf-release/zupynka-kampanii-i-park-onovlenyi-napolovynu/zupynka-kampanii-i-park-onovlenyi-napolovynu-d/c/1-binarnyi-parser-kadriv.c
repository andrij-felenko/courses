#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_UNKNOWN_FIELDS 32
#define MAX_PAYLOAD_SIZE 512

typedef enum {
    WIRE_VARINT = 0,
    WIRE_FIXED64 = 1,
    WIRE_LENGTH_DELIMITED = 2
} wire_type_t;

typedef struct {
    uint32_t tag;
    wire_type_t wire_type;
    uint32_t length;
    uint8_t payload[MAX_PAYLOAD_SIZE];
} unknown_field_t;

/* Структура повідомлення транзакції для вузла версії v1 */
typedef struct {
    uint64_t transaction_id;   /* Tag 1 (Обов'язкове поле v1) */
    uint64_t amount_cents;      /* Tag 2 (Обов'язкове поле v1) */
    uint64_t timestamp_utc;     /* Tag 3 (Обов'язкове поле v1) */
    
    unknown_field_t unknown_pool[MAX_UNKNOWN_FIELDS];
    size_t unknown_count;
} wire_transaction_msg_t;

/* Десеріалізація потоку байтів з ізоляцією невідомих тегів v2 */
bool parse_wire_frame(const uint8_t *src, size_t src_len, wire_transaction_msg_t *out_msg) {
    if (!src || !out_msg) return false;
    memset(out_msg, 0, sizeof(*out_msg));

    size_t cursor = 0;
    while (cursor < src_len) {
        if (cursor + 1 > src_len) return false;

        uint8_t header = src[cursor++];
        uint32_t tag = (uint32_t)(header >> 3);
        wire_type_t wtype = (wire_type_t)(header & 0x07);

        if (tag == 1 && wtype == WIRE_VARINT) {
            if (cursor + sizeof(uint64_t) > src_len) return false;
            memcpy(&out_msg->transaction_id, src + cursor, sizeof(uint64_t));
            cursor += sizeof(uint64_t);
        } else if (tag == 2 && wtype == WIRE_VARINT) {
            if (cursor + sizeof(uint64_t) > src_len) return false;
            memcpy(&out_msg->amount_cents, src + cursor, sizeof(uint64_t));
            cursor += sizeof(uint64_t);
        } else if (tag == 3 && wtype == WIRE_VARINT) {
            if (cursor + sizeof(uint64_t) > src_len) return false;
            memcpy(&out_msg->timestamp_utc, src + cursor, sizeof(uint64_t));
            cursor += sizeof(uint64_t);
        } else {
            /* Збереження невідомого поля нової версії коду */
            if (out_msg->unknown_count >= MAX_UNKNOWN_FIELDS) return false;

            unknown_field_t *uf = &out_msg->unknown_pool[out_msg->unknown_count];
            uf->tag = tag;
            uf->wire_type = wtype;

            if (wtype == WIRE_VARINT || wtype == WIRE_FIXED64) {
                uf->length = sizeof(uint64_t);
                if (cursor + uf->length > src_len) return false;
                memcpy(uf->payload, src + cursor, uf->length);
                cursor += uf->length;
            } else if (wtype == WIRE_LENGTH_DELIMITED) {
                if (cursor + 1 > src_len) return false;
                uf->length = src[cursor++];
                if (uf->length > MAX_PAYLOAD_SIZE || cursor + uf->length > src_len) return false;
                memcpy(uf->payload, src + cursor, uf->length);
                cursor += uf->length;
            } else {
                return false; /* Невідомий дріт-тип */
            }
            out_msg->unknown_count++;
        }
    }
    return true;
}

/* Повторна серіалізація зі збереженням структури v2 */
size_t serialize_wire_frame(const wire_transaction_msg_t *msg, uint8_t *dst, size_t dst_max) {
    if (!msg || !dst) return 0;
    size_t cursor = 0;

    /* Запис обов'язкових полів v1 */
    if (cursor + 1 + sizeof(uint64_t) > dst_max) return 0;
    dst[cursor++] = (uint8_t)((1 << 3) | WIRE_VARINT);
    memcpy(dst + cursor, &msg->transaction_id, sizeof(uint64_t));
    cursor += sizeof(uint64_t);

    if (cursor + 1 + sizeof(uint64_t) > dst_max) return 0;
    dst[cursor++] = (uint8_t)((2 << 3) | WIRE_VARINT);
    memcpy(dst + cursor, &msg->amount_cents, sizeof(uint64_t));
    cursor += sizeof(uint64_t);

    if (cursor + 1 + sizeof(uint64_t) > dst_max) return 0;
    dst[cursor++] = (uint8_t)((3 << 3) | WIRE_VARINT);
    memcpy(dst + cursor, &msg->timestamp_utc, sizeof(uint64_t));
    cursor += sizeof(uint64_t);

    /* Ретрансляція збережених невідомих полів */
    for (size_t i = 0; i < msg->unknown_count; ++i) {
        const unknown_field_t *uf = &msg->unknown_pool[i];
        if (cursor + 1 > dst_max) return 0;
        dst[cursor++] = (uint8_t)((uf->tag << 3) | uf->wire_type);

        if (uf->wire_type == WIRE_LENGTH_DELIMITED) {
            if (cursor + 1 > dst_max) return 0;
            dst[cursor++] = (uint8_t)uf->length;
        }
        if (cursor + uf->length > dst_max) return 0;
        memcpy(dst + cursor, uf->payload, uf->length);
        cursor += uf->length;
    }

    return cursor;
}
