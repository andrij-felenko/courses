/*
 * Кадр оновлення таблиці правил і двоетапна фіксація:
 * SOF(2) | Length(2) | Type(1) | Payload(N*16) | CRC-16(2).
 */
#ifndef RULE_FRAME_H
#define RULE_FRAME_H

#include "rule_engine.h"

#define FRAME_SOF_HI          0xAAu
#define FRAME_SOF_LO          0x55u
#define FRAME_TYPE_RULE_TABLE 0x01u
#define FRAME_TYPE_ACK        0x06u
#define FRAME_TYPE_NACK       0x15u

#define FRAME_HEADER_SIZE 5u   /* SOF + Length + Type */
#define FRAME_CRC_SIZE    2u
#define FRAME_MIN_SIZE    (FRAME_HEADER_SIZE + FRAME_CRC_SIZE)
#define FRAME_MAX_SIZE    (FRAME_HEADER_SIZE + MAX_RULES_COUNT * RULE_DESCRIPTOR_SIZE + FRAME_CRC_SIZE)
#define FRAME_REPLY_SIZE  (FRAME_HEADER_SIZE + 1u + FRAME_CRC_SIZE)

uint16_t rule_frame_crc16(const uint8_t *data, size_t len);

/* Складання кадру; повертає довжину або 0, якщо буфер замалий. */
size_t rule_frame_encode(uint8_t type, const uint8_t *payload, uint16_t payload_len,
                         uint8_t *out, size_t out_cap);
size_t rule_frame_encode_table(const rule_descriptor_t *table, uint8_t count,
                               uint8_t *out, size_t out_cap);

/* Повний цикл прийому: розбір → перевірки → атомарна фіксація → ACK/NACK. */
rule_error_t rule_frame_handle(rule_engine_t *e, const uint8_t *frame, size_t len,
                               uint8_t *reply, size_t reply_cap, size_t *reply_len);

const char *rule_error_str(rule_error_t err);

#endif /* RULE_FRAME_H */
