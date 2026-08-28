#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAVLINK_STX_V2 0xFD
#define MAVLINK_MAX_PAYLOAD_LEN 255
#define MAVLINK_NUM_CHECKSUM_BYTES 2
#define MAVLINK_SIGNATURE_LEN 13
#define MAVLINK_IFLAG_SIGNED 0x01

typedef enum {
    MAV_PARSE_STATE_IDLE,
    MAV_PARSE_STATE_GOT_STX,
    MAV_PARSE_STATE_GOT_LENGTH,
    MAV_PARSE_STATE_GOT_INCOMPAT_FLAGS,
    MAV_PARSE_STATE_GOT_COMPAT_FLAGS,
    MAV_PARSE_STATE_GOT_SEQ,
    MAV_PARSE_STATE_GOT_SYSID,
    MAV_PARSE_STATE_GOT_COMPID,
    MAV_PARSE_STATE_GOT_MSGID1,
    MAV_PARSE_STATE_GOT_MSGID2,
    MAV_PARSE_STATE_GOT_MSGID3,
    MAV_PARSE_STATE_GOT_PAYLOAD,
    MAV_PARSE_STATE_GOT_CRC1,
    MAV_PARSE_STATE_GOT_CRC2,
    MAV_PARSE_STATE_GOT_SIGNATURE
} mav_parse_state_t;

typedef struct {
    uint8_t magic;
    uint8_t len;
    uint8_t incompat_flags;
    uint8_t compat_flags;
    uint8_t seq;
    uint8_t sysid;
    uint8_t compid;
    uint32_t msgid;
    uint8_t payload[MAVLINK_MAX_PAYLOAD_LEN];
    uint16_t checksum;
    uint8_t signature[MAVLINK_SIGNATURE_LEN];
} mavlink_frame_t;

typedef struct {
    mav_parse_state_t state;
    mavlink_frame_t frame;
    uint16_t rx_count;
    uint16_t crc_accum;
    uint8_t sig_count;
} mavlink_parser_t;

static inline void crc_accumulate(uint8_t data, uint16_t *crcAccum) {
    uint8_t tmp = data ^ (uint8_t)(*crcAccum & 0xFF);
    tmp ^= (tmp << 4);
    *crcAccum = (*crcAccum >> 8) ^ ((uint16_t)tmp << 8) ^ ((uint16_t)tmp << 3) ^ ((uint16_t)tmp >> 4);
}

void mavlink_parser_init(mavlink_parser_t *p) {
    p->state = MAV_PARSE_STATE_IDLE;
    p->rx_count = 0;
    p->crc_accum = 0xFFFF;
    p->sig_count = 0;
    memset(&p->frame, 0, sizeof(p->frame));
}

bool mavlink_parse_byte(mavlink_parser_t *p, uint8_t byte, uint8_t crc_extra) {
    switch (p->state) {
    case MAV_PARSE_STATE_IDLE:
        if (byte == MAVLINK_STX_V2) {
            p->frame.magic = byte;
            p->crc_accum = 0xFFFF;
            p->state = MAV_PARSE_STATE_GOT_STX;
        }
        break;

    case MAV_PARSE_STATE_GOT_STX:
        p->frame.len = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_LENGTH;
        break;

    case MAV_PARSE_STATE_GOT_INCOMPAT_FLAGS:
        p->frame.incompat_flags = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_COMPAT_FLAGS;
        break;

    case MAV_PARSE_STATE_GOT_COMPAT_FLAGS:
        p->frame.compat_flags = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_SEQ;
        break;

    case MAV_PARSE_STATE_GOT_SEQ:
        p->frame.seq = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_SYSID;
        break;

    case MAV_PARSE_STATE_GOT_SYSID:
        p->frame.sysid = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_COMPID;
        break;

    case MAV_PARSE_STATE_GOT_COMPID:
        p->frame.compid = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_MSGID1;
        break;

    case MAV_PARSE_STATE_GOT_MSGID1:
        p->frame.msgid = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_MSGID2;
        break;

    case MAV_PARSE_STATE_GOT_MSGID2:
        p->frame.msgid |= ((uint32_t)byte << 8);
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_MSGID3;
        break;

    case MAV_PARSE_STATE_GOT_MSGID3:
        p->frame.msgid |= ((uint32_t)byte << 16);
        crc_accumulate(byte, &p->crc_accum);
        p->rx_count = 0;
        if (p->frame.len == 0) {
            p->state = MAV_PARSE_STATE_GOT_CRC1;
        } else {
            p->state = MAV_PARSE_STATE_GOT_PAYLOAD;
        }
        break;

    case MAV_PARSE_STATE_GOT_PAYLOAD:
        if (p->rx_count < p->frame.len) {
            p->frame.payload[p->rx_count++] = byte;
            crc_accumulate(byte, &p->crc_accum);
        }
        if (p->rx_count >= p->frame.len) {
            p->state = MAV_PARSE_STATE_GOT_CRC1;
        }
        break;

    case MAV_PARSE_STATE_GOT_CRC1:
        p->frame.checksum = byte;
        p->state = MAV_PARSE_STATE_GOT_CRC2;
        break;

    case MAV_PARSE_STATE_GOT_CRC2:
        p->frame.checksum |= ((uint16_t)byte << 8);
        crc_accumulate(crc_extra, &p->crc_accum);

        if (p->frame.checksum != p->crc_accum) {
            mavlink_parser_init(p);
            return false;
        }

        if (p->frame.incompat_flags & MAVLINK_IFLAG_SIGNED) {
            p->sig_count = 0;
            p->state = MAV_PARSE_STATE_GOT_SIGNATURE;
        } else {
            p->state = MAV_PARSE_STATE_IDLE;
            return true;
        }
        break;

    case MAV_PARSE_STATE_GOT_SIGNATURE:
        p->frame.signature[p->sig_count++] = byte;
        if (p->sig_count >= MAVLINK_SIGNATURE_LEN) {
            p->state = MAV_PARSE_STATE_IDLE;
            return true;
        }
        break;
    }
    return false;
}
