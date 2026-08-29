#include "frame.h"

#include "hal.h"

enum {
    ST_SOF = 0,
    ST_CMD,
    ST_LEN_LO,
    ST_LEN_HI,
    ST_PAYLOAD,
    ST_CRC_LO,
    ST_CRC_HI
};

uint16_t crc16_update(uint16_t crc, uint8_t byte)
{
    crc ^= (uint16_t)byte << 8;
    for (int bit = 0; bit < 8; bit++) {
        crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u) : (uint16_t)(crc << 1);
    }
    return crc;
}

void frame_rx_init(frame_rx_t *rx)
{
    rx->state = ST_SOF;
    rx->cmd = 0;
    rx->len = 0;
    rx->got = 0;
    rx->crc_calc = 0xFFFFu;
    rx->crc_recv = 0;
    rx->last_byte_ms = 0;
}

void frame_rx_watchdog(frame_rx_t *rx, uint32_t now_ms)
{
    if (rx->state != ST_SOF && (uint32_t)(now_ms - rx->last_byte_ms) > FRAME_GAP_MS) {
        frame_rx_init(rx);
    }
}

frame_rx_result_t frame_rx_push(frame_rx_t *rx, uint8_t byte, uint32_t now_ms, frame_t *out)
{
    /* Обрив передачі посеред кадру не має злипатися з наступним кадром */
    frame_rx_watchdog(rx, now_ms);
    rx->last_byte_ms = now_ms;

    switch (rx->state) {
    case ST_SOF:
        if (byte == FRAME_SOF) {
            rx->crc_calc = 0xFFFFu;
            rx->state = ST_CMD;
        }
        return FRAME_RX_PENDING;

    case ST_CMD:
        rx->cmd = byte;
        rx->crc_calc = crc16_update(rx->crc_calc, byte);
        rx->state = ST_LEN_LO;
        return FRAME_RX_PENDING;

    case ST_LEN_LO:
        rx->len = byte;
        rx->crc_calc = crc16_update(rx->crc_calc, byte);
        rx->state = ST_LEN_HI;
        return FRAME_RX_PENDING;

    case ST_LEN_HI:
        rx->len |= (uint16_t)byte << 8;
        rx->crc_calc = crc16_update(rx->crc_calc, byte);
        if (rx->len > FRAME_MAX_PAYLOAD) {
            frame_rx_init(rx);
            return FRAME_RX_OVERFLOW;
        }
        rx->got = 0;
        rx->state = (rx->len == 0) ? ST_CRC_LO : ST_PAYLOAD;
        return FRAME_RX_PENDING;

    case ST_PAYLOAD:
        rx->payload[rx->got++] = byte;
        rx->crc_calc = crc16_update(rx->crc_calc, byte);
        if (rx->got == rx->len) {
            rx->state = ST_CRC_LO;
        }
        return FRAME_RX_PENDING;

    case ST_CRC_LO:
        rx->crc_recv = byte;
        rx->state = ST_CRC_HI;
        return FRAME_RX_PENDING;

    case ST_CRC_HI: {
        rx->crc_recv |= (uint16_t)byte << 8;

        const uint16_t expected = rx->crc_calc;
        const uint16_t received = rx->crc_recv;

        out->cmd = rx->cmd;
        out->len = rx->len;
        for (uint16_t i = 0; i < rx->len; i++) {
            out->payload[i] = rx->payload[i];
        }
        frame_rx_init(rx);

        return (expected == received) ? FRAME_RX_DONE : FRAME_RX_BAD_CRC;
    }

    default:
        frame_rx_init(rx);
        return FRAME_RX_PENDING;
    }
}

void frame_send(uint8_t cmd, const uint8_t *payload, uint16_t len)
{
    uint8_t header[4] = {
        FRAME_SOF,
        cmd,
        (uint8_t)(len & 0xFFu),
        (uint8_t)(len >> 8),
    };

    uint16_t crc = 0xFFFFu;
    for (size_t i = 1; i < sizeof header; i++) {
        crc = crc16_update(crc, header[i]);
    }
    for (uint16_t i = 0; i < len; i++) {
        crc = crc16_update(crc, payload[i]);
    }

    uint8_t tail[2] = { (uint8_t)(crc & 0xFFu), (uint8_t)(crc >> 8) };

    hal_uart_write(header, sizeof header);
    if (len != 0) {
        hal_uart_write(payload, len);
    }
    hal_uart_write(tail, sizeof tail);
}
