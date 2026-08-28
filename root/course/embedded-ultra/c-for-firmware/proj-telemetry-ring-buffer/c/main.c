#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FRAME_START_BYTE 0xAAU
#define FRAME_END_BYTE   0x55U

// --- Структура корисного навантаження без проміжних байтів ---
typedef struct __attribute__((packed)) {
    uint8_t  node_id;
    uint32_t timestamp_ms;
    int16_t  accel_x;
    int16_t  accel_y;
    int16_t  accel_z;
    uint16_t voltage_mv;
    uint16_t sequence_id;
} TelemetryPayload;

#define PAYLOAD_SIZE sizeof(TelemetryPayload)
_Static_assert(PAYLOAD_SIZE == 15, "Payload size must be exactly 15 bytes!");

// --- Статичний кільцевий буфер SPSC ---
#define RX_BUF_SIZE 256U
#define RX_BUF_MASK (RX_BUF_SIZE - 1U)

typedef struct {
    uint8_t buffer[RX_BUF_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} RingBuffer;

static RingBuffer rx_ring;

static inline bool ring_put(RingBuffer *rb, uint8_t byte) {
    uint16_t next = (uint16_t)((rb->head + 1U) & RX_BUF_MASK);
    if (next == rb->tail) {
        return false; // Буфер переповнено
    }
    rb->buffer[rb->head] = byte;
    rb->head = next;
    return true;
}

static inline bool ring_get(RingBuffer *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return false; // Буфер порожній
    }
    *byte = rb->buffer[rb->tail];
    rb->tail = (uint16_t)((rb->tail + 1U) & RX_BUF_MASK);
    return true;
}

// --- Розрахунок контрольної суми CRC-16-CCITT ---
static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000U) {
                crc = (uint16_t)((crc << 1) ^ 0x1021U);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

// --- Апаратний обробник переривання UART (ISR) ---
void USART1_IRQHandler(void) {
    volatile uint32_t *uart_sr = (volatile uint32_t *)0x40013800UL;
    volatile uint32_t *uart_dr = (volatile uint32_t *)0x40013804UL;

    if (*uart_sr & (1U << 5)) { // Прапорець RXNE (байт готовий)
        uint8_t byte = (uint8_t)(*uart_dr & 0xFFU);
        ring_put(&rx_ring, byte);
    }
}

// --- Скінченний автомат розбору пакетів ---
typedef enum {
    PARSER_WAIT_START,
    PARSER_READ_PAYLOAD,
    PARSER_READ_CRC_LOW,
    PARSER_READ_CRC_HIGH,
    PARSER_WAIT_END
} ParserState;

typedef struct {
    ParserState state;
    uint8_t payload_raw[PAYLOAD_SIZE];
    uint8_t bytes_read;
    uint16_t rx_crc;
    uint32_t packets_received;
    uint32_t crc_errors;
} TelemetryParser;

static TelemetryParser parser;

void telemetry_process_packet(const TelemetryPayload *packet) {
    // Безпечна обробка валідованого кадру в super-loop
    (void)packet;
}

void telemetry_parser_poll(void) {
    uint8_t byte;
    while (ring_get(&rx_ring, &byte)) {
        switch (parser.state) {
            case PARSER_WAIT_START:
                if (byte == FRAME_START_BYTE) {
                    parser.bytes_read = 0;
                    parser.state = PARSER_READ_PAYLOAD;
                }
                break;

            case PARSER_READ_PAYLOAD:
                parser.payload_raw[parser.bytes_read++] = byte;
                if (parser.bytes_read >= PAYLOAD_SIZE) {
                    parser.state = PARSER_READ_CRC_LOW;
                }
                break;

            case PARSER_READ_CRC_LOW:
                parser.rx_crc = byte;
                parser.state = PARSER_READ_CRC_HIGH;
                break;

            case PARSER_READ_CRC_HIGH:
                parser.rx_crc |= (uint16_t)((uint16_t)byte << 8);
                parser.state = PARSER_WAIT_END;
                break;

            case PARSER_WAIT_END:
                if (byte == FRAME_END_BYTE) {
                    uint16_t calc_crc = crc16_ccitt(parser.payload_raw, PAYLOAD_SIZE);
                    if (calc_crc == parser.rx_crc) {
                        TelemetryPayload packet;
                        memcpy(&packet, parser.payload_raw, sizeof(packet));
                        parser.packets_received++;
                        telemetry_process_packet(&packet);
                    } else {
                        parser.crc_errors++;
                    }
                }
                parser.state = PARSER_WAIT_START;
                break;
        }
    }
}
