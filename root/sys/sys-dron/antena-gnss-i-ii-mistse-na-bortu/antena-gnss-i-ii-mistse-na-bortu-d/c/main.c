#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define UBX_SYNC_1 0xB5
#define UBX_SYNC_2 0x62
#define UBX_CLASS_MON 0x0A
#define UBX_ID_MON_RF 0x38

typedef enum {
    PARSE_SYNC1,
    PARSE_SYNC2,
    PARSE_CLASS,
    PARSE_ID,
    PARSE_LEN_L,
    PARSE_LEN_H,
    PARSE_PAYLOAD,
    PARSE_CK_A,
    PARSE_CK_B
} ubx_step_t;

typedef struct {
    uint8_t block_id;
    uint16_t noise_per_ms;
    uint16_t agc_cnt;
    uint8_t jam_ind;
    uint8_t jamming_state;
} rf_block_data_t;

typedef struct {
    ubx_step_t step;
    uint8_t msg_class;
    uint8_t msg_id;
    uint16_t length;
    uint16_t index;
    uint8_t buffer[128];
    uint8_t ck_a;
    uint8_t ck_b;
    uint8_t calc_a;
    uint8_t calc_b;
} ubx_stream_parser_t;

void ubx_stream_init(ubx_stream_parser_t *p) {
    p->step = PARSE_SYNC1;
    p->calc_a = 0;
    p->calc_b = 0;
}

bool ubx_stream_parse(ubx_stream_parser_t *p, uint8_t byte, rf_block_data_t *out_data) {
    switch (p->step) {
        case PARSE_SYNC1:
            if (byte == UBX_SYNC_1) p->step = PARSE_SYNC2;
            break;
        case PARSE_SYNC2:
            if (byte == UBX_SYNC_2) {
                p->step = PARSE_CLASS;
                p->calc_a = 0;
                p->calc_b = 0;
            } else {
                p->step = PARSE_SYNC1;
            }
            break;
        case PARSE_CLASS:
            p->msg_class = byte;
            p->calc_a += byte; p->calc_b += p->calc_a;
            p->step = PARSE_ID;
            break;
        case PARSE_ID:
            p->msg_id = byte;
            p->calc_a += byte; p->calc_b += p->calc_a;
            p->step = PARSE_LEN_L;
            break;
        case PARSE_LEN_L:
            p->length = byte;
            p->calc_a += byte; p->calc_b += p->calc_a;
            p->step = PARSE_LEN_H;
            break;
        case PARSE_LEN_H:
            p->length |= (uint16_t)(byte << 8);
            p->calc_a += byte; p->calc_b += p->calc_a;
            p->index = 0;
            if (p->length > sizeof(p->buffer) || p->length < 4) {
                p->step = PARSE_SYNC1;
            } else {
                p->step = PARSE_PAYLOAD;
            }
            break;
        case PARSE_PAYLOAD:
            p->buffer[p->index++] = byte;
            p->calc_a += byte; p->calc_b += p->calc_a;
            if (p->index >= p->length) p->step = PARSE_CK_A;
            break;
        case PARSE_CK_A:
            p->ck_a = byte;
            p->step = PARSE_CK_B;
            break;
        case PARSE_CK_B:
            p->ck_b = byte;
            p->step = PARSE_SYNC1;
            if (p->ck_a == p->calc_a && p->ck_b == p->calc_b) {
                if (p->msg_class == UBX_CLASS_MON && p->msg_id == UBX_ID_MON_RF) {
                    uint8_t n_blocks = p->buffer[1];
                    if (n_blocks > 0 && p->length >= 28) {
                        out_data->block_id = p->buffer[4];
                        out_data->noise_per_ms = (uint16_t)(p->buffer[12] | (p->buffer[13] << 8));
                        out_data->agc_cnt = (uint16_t)(p->buffer[14] | (p->buffer[15] << 8));
                        out_data->jam_ind = p->buffer[16];
                        out_data->jamming_state = p->buffer[18];
                        return true;
                    }
                }
            }
            break;
    }
    return false;
}
