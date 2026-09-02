#ifndef CRSF_H
#define CRSF_H

#include <stddef.h>
#include <stdint.h>

#include "rc_channels.h"

/* Кадр RC_CHANNELS_PACKED протоколу CRSF (ExpressLRS / TBS Crossfire) */

#define CRSF_ADDR_FLIGHT_CONTROLLER       0xC8U
#define CRSF_FRAMETYPE_RC_CHANNELS_PACKED 0x16U
#define CRSF_CRC_POLY                     0xD5U

/* адреса + довжина + тип + 22 байти каналів + CRC8 */
#define CRSF_RC_FRAME_SIZE   26U
#define CRSF_RC_LENGTH_FIELD 24U   /* тип + канали + CRC */

typedef enum {
    CRSF_OK = 0,
    CRSF_ERR_ARGS,
    CRSF_ERR_SIZE,
    CRSF_ERR_ADDRESS,
    CRSF_ERR_LENGTH,
    CRSF_ERR_TYPE,
    CRSF_ERR_CRC
} crsf_status_t;

/* CRC8 з поліномом 0xD5 (DVB-S2), рахується від байта типу включно */
uint8_t crsf_crc8(const uint8_t *data, size_t len);

crsf_status_t crsf_parse_rc_frame(const uint8_t *frame, size_t len,
                                  uint16_t raw[RC_TOTAL_CHANNELS]);

/* Збирає кадр так, як його вивів би передавач; повертає довжину або 0 */
size_t crsf_build_rc_frame(const uint16_t raw[RC_TOTAL_CHANNELS],
                           uint8_t frame[CRSF_RC_FRAME_SIZE]);

const char *crsf_status_text(crsf_status_t status);

#endif /* CRSF_H */
