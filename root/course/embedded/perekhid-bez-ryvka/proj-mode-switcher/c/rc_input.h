#ifndef RC_INPUT_H
#define RC_INPUT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* CRSF, кадр RC_CHANNELS_PACKED: адреса, довжина, тип, 22 байти каналів, CRC8. */
#define RC_CHANNEL_COUNT 16
#define RC_FRAME_SIZE    26
#define RC_PAYLOAD_LEN   24u   /* тип + 22 байти даних + crc */
#define RC_ADDR_FC       0xC8u /* адреса польотного контролера */
#define RC_TYPE_CHANNELS 0x16u
#define RC_FAILSAFE_MS   500u

typedef enum {
    RC_OK = 0,
    RC_ERR_SHORT,
    RC_ERR_ADDR,
    RC_ERR_LEN,
    RC_ERR_TYPE,
    RC_ERR_CRC
} rc_err_t;

typedef struct { uint16_t ch[RC_CHANNEL_COUNT]; } rc_channels_t;

typedef struct {
    rc_channels_t ch;       /* останній кадр, що пройшов перевірку */
    uint32_t last_ok_ms;
    bool     have_data;
    bool     failsafe;
    unsigned frames_ok;
    unsigned crc_errors;
    unsigned format_errors;
} rc_link_t;

uint8_t  rc_crc8(const uint8_t *data, size_t len);
rc_err_t rc_frame_parse(const uint8_t *frame, size_t len, rc_channels_t *out);
void     rc_frame_build(const rc_channels_t *ch, uint8_t frame[RC_FRAME_SIZE]);

float rc_channel_us(uint16_t raw);
float rc_channel_unit(uint16_t raw);           /* 0..1 */
int   rc_switch_pos(float us, int prev_pos);   /* 3 позиції AUX1 з гістерезисом */

void     rc_link_init(rc_link_t *l, uint32_t now_ms);
rc_err_t rc_link_feed(rc_link_t *l, const uint8_t *frame, size_t len, uint32_t now_ms);
bool     rc_link_tick(rc_link_t *l, uint32_t now_ms);  /* true = втрата зв'язку */

#endif /* RC_INPUT_H */
