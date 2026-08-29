#ifndef EOLBOOT_FRAME_H
#define EOLBOOT_FRAME_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/*
 * Кадр діагностичного порту:
 *   0x55 | cmd | len_lo | len_hi | payload[len] | crc_lo | crc_hi
 * CRC-16/CCITT рахується від cmd до останнього байта payload.
 */

#define FRAME_SOF         0x55u
#define FRAME_MAX_PAYLOAD 96u
#define FRAME_GAP_MS      1000u

typedef enum {
    CMD_GET_CHALLENGE  = 0x01, /* хост -> пристрій */
    CMD_UNLOCK_EXECUTE = 0x02, /* хост -> пристрій, payload = підпис 64 байти */
    CMD_CHALLENGE      = 0x81, /* пристрій -> хост, payload = Nonce || Chip_UUID */
    CMD_STATUS         = 0x82  /* пристрій -> хост, payload = один байт коду */
} frame_cmd_t;

typedef enum {
    FRAME_RX_PENDING,  /* кадр іще збирається */
    FRAME_RX_DONE,
    FRAME_RX_BAD_CRC,
    FRAME_RX_OVERFLOW  /* заявлена довжина більша за буфер */
} frame_rx_result_t;

typedef struct {
    uint8_t  cmd;
    uint16_t len;
    uint8_t  payload[FRAME_MAX_PAYLOAD];
} frame_t;

typedef struct {
    uint8_t  state;
    uint8_t  cmd;
    uint16_t len;
    uint16_t got;
    uint16_t crc_calc;
    uint16_t crc_recv;
    uint32_t last_byte_ms;
    uint8_t  payload[FRAME_MAX_PAYLOAD];
} frame_rx_t;

void frame_rx_init(frame_rx_t *rx);

/* Приймає один байт; при FRAME_RX_DONE зібраний кадр лежить в out */
frame_rx_result_t frame_rx_push(frame_rx_t *rx, uint8_t byte, uint32_t now_ms, frame_t *out);

/* Кидає недозібраний кадр, якщо хост замовк посеред передачі */
void frame_rx_watchdog(frame_rx_t *rx, uint32_t now_ms);

void frame_send(uint8_t cmd, const uint8_t *payload, uint16_t len);

uint16_t crc16_update(uint16_t crc, uint8_t byte);

#endif /* EOLBOOT_FRAME_H */
