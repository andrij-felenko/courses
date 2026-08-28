#ifndef COBS_H
#define COBS_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    COBS_OK = 0,
    COBS_ERR_NULL_PTR,
    COBS_ERR_BUFFER_OVERFLOW,
    COBS_ERR_ZERO_IN_PAYLOAD,
    COBS_ERR_UNEXPECTED_DELIMITER,
    COBS_ERR_INVALID_OFFSET
} cobs_status_t;

typedef enum {
    COBS_STATE_HUNT_DELIMITER = 0,
    COBS_STATE_READ_CODE,
    COBS_STATE_READ_DATA
} cobs_parser_state_t;

typedef struct {
    uint8_t *rx_buf;
    size_t rx_capacity;
    size_t rx_len;
    cobs_parser_state_t state;
    uint8_t code;
    uint8_t block_rem;
} cobs_parser_t;

/**
 * Блокове кодування масиву байтів.
 * @param src Вказівник на вхідний масив.
 * @param src_len Довжина вхідного масиву.
 * @param dst Вказівник на вихідний буфер (розмір >= src_len + src_len/254 + 1).
 * @param dst_capacity Місткість вихідного буфера.
 * @param out_len Вказівник для повернення фактичної кількості записаних байтів.
 */
cobs_status_t cobs_encode(const uint8_t *src, size_t src_len, 
                          uint8_t *dst, size_t dst_capacity, size_t *out_len);

/**
 * Блокове декодування масиву (підтримує in-place при src == dst).
 */
cobs_status_t cobs_decode(const uint8_t *src, size_t src_len, 
                          uint8_t *dst, size_t dst_capacity, size_t *out_len);

/**
 * Ініціалізація потокового парсера.
 */
void cobs_parser_init(cobs_parser_t *parser, uint8_t *buffer, size_t capacity);

/**
 * Обробка одного байта, отриманого з UART/DMA.
 * @return true, якщо зібрано повний валідний пакет.
 */
bool cobs_parser_feed_byte(cobs_parser_t *parser, uint8_t byte, cobs_status_t *status);

#ifdef __cplusplus
}
#endif

#endif // COBS_H

// --- cobs.c ---
#include <string.h>

cobs_status_t cobs_encode(const uint8_t *src, size_t src_len, 
                          uint8_t *dst, size_t dst_capacity, size_t *out_len) {
    if (!src || !dst || !out_len) return COBS_ERR_NULL_PTR;

    size_t max_req = src_len + (src_len / 254) + 1;
    if (dst_capacity < max_req) return COBS_ERR_BUFFER_OVERFLOW;

    size_t read_idx = 0;
    size_t write_idx = 1;
    size_t code_idx = 0;
    uint8_t code = 0x01;

    while (read_idx < src_len) {
        uint8_t byte = src[read_idx++];
        if (byte == 0x00) {
            dst[code_idx] = code;
            code_idx = write_idx++;
            code = 0x01;
        } else {
            dst[write_idx++] = byte;
            code++;
            if (code == 0xFF) {
                dst[code_idx] = code;
                code_idx = write_idx++;
                code = 0x01;
            }
        }
    }
    dst[code_idx] = code;
    *out_len = write_idx;
    return COBS_OK;
}

cobs_status_t cobs_decode(const uint8_t *src, size_t src_len, 
                          uint8_t *dst, size_t dst_capacity, size_t *out_len) {
    if (!src || !dst || !out_len) return COBS_ERR_NULL_PTR;
    if (src_len == 0) {
        *out_len = 0;
        return COBS_OK;
    }

    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < src_len) {
        uint8_t code = src[read_idx++];
        if (code == 0x00) return COBS_ERR_ZERO_IN_PAYLOAD;

        uint8_t copy_len = code - 1;
        if (read_idx + copy_len > src_len) return COBS_ERR_INVALID_OFFSET;
        if (write_idx + copy_len > dst_capacity) return COBS_ERR_BUFFER_OVERFLOW;

        for (uint8_t i = 0; i < copy_len; ++i) {
            dst[write_idx++] = src[read_idx++];
        }

        if (code < 0xFF && read_idx < src_len) {
            if (write_idx >= dst_capacity) return COBS_ERR_BUFFER_OVERFLOW;
            dst[write_idx++] = 0x00;
        }
    }

    *out_len = write_idx;
    return COBS_OK;
}

void cobs_parser_init(cobs_parser_t *parser, uint8_t *buffer, size_t capacity) {
    if (!parser) return;
    parser->rx_buf = buffer;
    parser->rx_capacity = capacity;
    parser->rx_len = 0;
    parser->state = COBS_STATE_HUNT_DELIMITER;
    parser->code = 0;
    parser->block_rem = 0;
}

bool cobs_parser_feed_byte(cobs_parser_t *parser, uint8_t byte, cobs_status_t *status) {
    if (!parser || !parser->rx_buf) {
        if (status) *status = COBS_ERR_NULL_PTR;
        return false;
    }

    // Зустріч із розділювачем кінця кадру
    if (byte == 0x00) {
        if (parser->state == COBS_STATE_READ_DATA && parser->block_rem > 0) {
            parser->rx_len = 0;
            parser->state = COBS_STATE_READ_CODE;
            if (status) *status = COBS_ERR_UNEXPECTED_DELIMITER;
            return false;
        }

        if (parser->rx_len > 0) {
            parser->state = COBS_STATE_READ_CODE;
            if (status) *status = COBS_OK;
            return true;
        }

        parser->state = COBS_STATE_READ_CODE;
        if (status) *status = COBS_OK;
        return false;
    }

    switch (parser->state) {
    case COBS_STATE_HUNT_DELIMITER:
        break;

    case COBS_STATE_READ_CODE:
        parser->code = byte;
        if (parser->code == 0x01) {
            if (parser->rx_len >= parser->rx_capacity) {
                parser->rx_len = 0;
                parser->state = COBS_STATE_HUNT_DELIMITER;
                if (status) *status = COBS_ERR_BUFFER_OVERFLOW;
                return false;
            }
            parser->rx_buf[parser->rx_len++] = 0x00;
        } else {
            parser->block_rem = parser->code - 1;
            parser->state = COBS_STATE_READ_DATA;
        }
        break;

    case COBS_STATE_READ_DATA:
        if (parser->rx_len >= parser->rx_capacity) {
            parser->rx_len = 0;
            parser->state = COBS_STATE_HUNT_DELIMITER;
            if (status) *status = COBS_ERR_BUFFER_OVERFLOW;
            return false;
        }

        parser->rx_buf[parser->rx_len++] = byte;
        parser->block_rem--;

        if (parser->block_rem == 0) {
            if (parser->code < 0xFF) {
                if (parser->rx_len >= parser->rx_capacity) {
                    parser->rx_len = 0;
                    parser->state = COBS_STATE_HUNT_DELIMITER;
                    if (status) *status = COBS_ERR_BUFFER_OVERFLOW;
                    return false;
                }
                parser->rx_buf[parser->rx_len++] = 0x00;
            }
            parser->state = COBS_STATE_READ_CODE;
        }
        break;
    }

    if (status) *status = COBS_OK;
    return false;
}
