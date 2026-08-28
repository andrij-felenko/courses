#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define PROTOCOL_MAGIC_BYTE 0x5A
#define MAX_PAYLOAD_LEN     128
#define HEADER_OVERHEAD     4 /* Magic(1B) + Seq(1B) + Type(1B) + Len(1B) */

/* Стани кінцевого автомата приймача */
typedef enum {
    RX_STATE_WAIT_MAGIC = 0,
    RX_STATE_READ_HEADER,
    RX_STATE_READ_PAYLOAD,
    RX_STATE_READ_CRC
} RxState_t;

typedef struct {
    uint8_t seq_num;
    uint8_t msg_type;
    uint8_t payload_len;
    uint8_t payload[MAX_PAYLOAD_LEN];
    uint16_t crc16;
} ProtocolPacket_t;

typedef struct {
    RxState_t state;
    uint8_t   rx_buf[HEADER_OVERHEAD + MAX_PAYLOAD_LEN + 2];
    size_t    bytes_needed;
    size_t    bytes_read;
    ProtocolPacket_t current_packet;
    uint32_t  stat_crc_errors;
    uint32_t  stat_len_overflows;
    uint32_t  stat_valid_frames;
} ProtocolReceiver_t;

/* Обчислення CRC-16 (поліном 0x1021) */
static uint16_t calc_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

void protocol_receiver_init(ProtocolReceiver_t *rx) {
    memset(rx, 0, sizeof(ProtocolReceiver_t));
    rx->state = RX_STATE_WAIT_MAGIC;
}

/*
 * Побайтова обробка вхідного потоку кінцевим автоматом.
 * Повертає true, коли успішно зібрано та перевірено повний кадр.
 */
bool protocol_receiver_feed_byte(ProtocolReceiver_t *rx, uint8_t byte, ProtocolPacket_t *out_pkt) {
    switch (rx->state) {
        case RX_STATE_WAIT_MAGIC:
            if (byte == PROTOCOL_MAGIC_BYTE) {
                rx->rx_buf[0] = byte;
                rx->bytes_read = 1;
                rx->bytes_needed = HEADER_OVERHEAD;
                rx->state = RX_STATE_READ_HEADER;
            }
            break;

        case RX_STATE_READ_HEADER:
            rx->rx_buf[rx->bytes_read++] = byte;
            if (rx->bytes_read == rx->bytes_needed) {
                rx->current_packet.seq_num = rx->rx_buf[1];
                rx->current_packet.msg_type = rx->rx_buf[2];
                rx->current_packet.payload_len = rx->rx_buf[3];

                if (rx->current_packet.payload_len > MAX_PAYLOAD_LEN) {
                    /* Захист від переповнення буфера: скид автомата */
                    rx->stat_len_overflows++;
                    rx->state = RX_STATE_WAIT_MAGIC;
                    break;
                }

                if (rx->current_packet.payload_len > 0) {
                    rx->bytes_needed += rx->current_packet.payload_len;
                    rx->state = RX_STATE_READ_PAYLOAD;
                } else {
                    rx->bytes_needed += 2; /* Тільки CRC-16 */
                    rx->state = RX_STATE_READ_CRC;
                }
            }
            break;

        case RX_STATE_READ_PAYLOAD:
            rx->rx_buf[rx->bytes_read++] = byte;
            if (rx->bytes_read == rx->bytes_needed) {
                memcpy(rx->current_packet.payload, &rx->rx_buf[HEADER_OVERHEAD], rx->current_packet.payload_len);
                rx->bytes_needed += 2; /* Переходимо до читання 2 байтів CRC */
                rx->state = RX_STATE_READ_CRC;
            }
            break;

        case RX_STATE_READ_CRC:
            rx->rx_buf[rx->bytes_read++] = byte;
            if (rx->bytes_read == rx->bytes_needed) {
                size_t crc_offset = rx->bytes_read - 2;
                uint16_t received_crc = (uint16_t)rx->rx_buf[crc_offset] |
                                        ((uint16_t)rx->rx_buf[crc_offset + 1] << 8);

                uint16_t expected_crc = calc_crc16(&rx->rx_buf[1], crc_offset - 1);

                if (received_crc == expected_crc) {
                    rx->current_packet.crc16 = received_crc;
                    *out_pkt = rx->current_packet;
                    rx->stat_valid_frames++;
                    rx->state = RX_STATE_WAIT_MAGIC;
                    return true;
                } else {
                    rx->stat_crc_errors++;
                    rx->state = RX_STATE_WAIT_MAGIC;
                }
            }
            break;
    }

    return false;
}
