/* Обробник та валідатор пакетів STK500 v2 (C99) */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define STK500_START_BYTE 0x1B
#define STK500_TOKEN_BYTE 0x0E
#define MAX_PAYLOAD_SIZE  275

typedef enum {
    STK_STATE_IDLE,
    STK_STATE_SEQ,
    STK_STATE_SIZE_H,
    STK_STATE_SIZE_L,
    STK_STATE_TOKEN,
    STK_STATE_PAYLOAD,
    STK_STATE_CHECKSUM
} stk_parser_state_t;

typedef struct {
    stk_parser_state_t state;
    uint8_t seq_num;
    uint16_t msg_size;
    uint16_t bytes_read;
    uint8_t calc_checksum;
    uint8_t payload[MAX_PAYLOAD_SIZE];
} stk500_parser_t;

void stk500_init(stk500_parser_t *p) {
    if (!p) return;
    p->state = STK_STATE_IDLE;
    p->seq_num = 0;
    p->msg_size = 0;
    p->bytes_read = 0;
    p->calc_checksum = 0;
}

/* Потоковий парсер вхідних байтів із послідовного порту UART */
bool stk500_parse_byte(stk500_parser_t *p, uint8_t byte, bool *packet_ready) {
    *packet_ready = false;
    
    switch (p->state) {
        case STK_STATE_IDLE:
            if (byte == STK500_START_BYTE) {
                p->calc_checksum = STK500_START_BYTE;
                p->state = STK_STATE_SEQ;
            }
            break;
            
        case STK_STATE_SEQ:
            p->seq_num = byte;
            p->calc_checksum ^= byte;
            p->state = STK_STATE_SIZE_H;
            break;
            
        case STK_STATE_SIZE_H:
            p->msg_size = (uint16_t)(byte << 8);
            p->calc_checksum ^= byte;
            p->state = STK_STATE_SIZE_L;
            break;
            
        case STK_STATE_SIZE_L:
            p->msg_size |= byte;
            p->calc_checksum ^= byte;
            if (p->msg_size > MAX_PAYLOAD_SIZE || p->msg_size == 0) {
                p->state = STK_STATE_IDLE; /* Помилка розміру пакету */
            } else {
                p->state = STK_STATE_TOKEN;
            }
            break;
            
        case STK_STATE_TOKEN:
            if (byte == STK500_TOKEN_BYTE) {
                p->calc_checksum ^= byte;
                p->bytes_read = 0;
                p->state = STK_STATE_PAYLOAD;
            } else {
                p->state = STK_STATE_IDLE; /* Збій токена */
            }
            break;
            
        case STK_STATE_PAYLOAD:
            p->payload[p->bytes_read++] = byte;
            p->calc_checksum ^= byte;
            if (p->bytes_read >= p->msg_size) {
                p->state = STK_STATE_CHECKSUM;
            }
            break;
            
        case STK_STATE_CHECKSUM:
            p->state = STK_STATE_IDLE;
            if (byte == p->calc_checksum) {
                *packet_ready = true;
                return true; /* Пакет успішно валідовано */
            }
            return false; /* Помилка контрольної суми */
    }
    return true;
}
