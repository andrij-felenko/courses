/* ============================================================================
 * telemetry_protocol.h — Публічний C-інтерфейс кодека протоколу (C99)
 * ============================================================================ */
#ifndef TELEMETRY_PROTOCOL_H
#define TELEMETRY_PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define PROTOCOL_PREAMBLE_1      0xAA
#define PROTOCOL_PREAMBLE_2      0x55
#define PROTOCOL_MAX_PAYLOAD     64
#define PROTOCOL_HEADER_SIZE     5
#define PROTOCOL_CRC_SIZE        2
#define PROTOCOL_MAX_FRAME_SIZE  (PROTOCOL_HEADER_SIZE + PROTOCOL_MAX_PAYLOAD + PROTOCOL_CRC_SIZE)

/* Коди повернення потокового парсера */
typedef enum {
    PARSER_STATE_CONTINUE = 0, /* Автомат очікує надходження наступних байтів */
    PARSER_STATE_COMPLETE = 1, /* Успішно прийнято та верифіковано повний пакет */
    PARSER_ERROR_CRC      = 2, /* Помилка контрольної суми CRC-16: пакет відкинуто */
    PARSER_ERROR_LENGTH   = 3  /* Помилка довжини: значення LEN перевищує буфер */
} parser_status_t;

/* Структура декодованого пакета */
typedef struct {
    uint8_t  msg_id;
    uint8_t  seq;
    uint8_t  len;
    uint8_t  payload[PROTOCOL_MAX_PAYLOAD];
} packet_t;

/* Стан потокового кінцевого автомата */
typedef struct {
    uint8_t   state;
    uint8_t   rx_index;
    uint16_t  running_crc;
    uint16_t  received_crc;
    packet_t  current_packet;
} parser_t;

/* Ініціалізація внутрішніх полів автомата */
void parser_init(parser_t *p);

/* Побайтове згодовування вхідного потоку автомату */
parser_status_t parser_consume_byte(parser_t *p, uint8_t byte, packet_t *out_packet);

/* Серіалізація заголовка, навантаження та розрахунок CRC */
size_t serialize_packet(uint8_t msg_id, uint8_t seq, const uint8_t *payload, uint8_t len, uint8_t *out_buf);

#endif /* TELEMETRY_PROTOCOL_H */
