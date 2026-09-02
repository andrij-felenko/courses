#include "crsf.h"

#include <stddef.h>

uint8_t crsf_crc8(const uint8_t *data, size_t len)
{
    uint8_t crc = 0U;

    if (data == NULL) {
        return 0U;
    }
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (unsigned bit = 0; bit < 8U; ++bit) {
            crc = (uint8_t)((crc & 0x80U) ? ((crc << 1) ^ CRSF_CRC_POLY) : (crc << 1));
        }
    }
    return crc;
}

crsf_status_t crsf_parse_rc_frame(const uint8_t *frame, size_t len,
                                  uint16_t raw[RC_TOTAL_CHANNELS])
{
    if (frame == NULL || raw == NULL) {
        return CRSF_ERR_ARGS;
    }
    if (len < CRSF_RC_FRAME_SIZE) {
        return CRSF_ERR_SIZE;
    }
    if (frame[0] != CRSF_ADDR_FLIGHT_CONTROLLER) {
        return CRSF_ERR_ADDRESS;
    }
    if (frame[1] != CRSF_RC_LENGTH_FIELD) {
        return CRSF_ERR_LENGTH;
    }
    if (frame[2] != CRSF_FRAMETYPE_RC_CHANNELS_PACKED) {
        return CRSF_ERR_TYPE;
    }

    /* CRC покриває тип і корисне навантаження: байти 2..24 включно */
    uint8_t crc = crsf_crc8(&frame[2], 1U + RC_PACKED_BYTES);
    if (crc != frame[CRSF_RC_FRAME_SIZE - 1U]) {
        return CRSF_ERR_CRC;
    }

    rc_unpack_11bit(&frame[3], raw);
    return CRSF_OK;
}

size_t crsf_build_rc_frame(const uint16_t raw[RC_TOTAL_CHANNELS],
                           uint8_t frame[CRSF_RC_FRAME_SIZE])
{
    if (raw == NULL || frame == NULL) {
        return 0U;
    }

    frame[0] = CRSF_ADDR_FLIGHT_CONTROLLER;
    frame[1] = CRSF_RC_LENGTH_FIELD;
    frame[2] = CRSF_FRAMETYPE_RC_CHANNELS_PACKED;
    rc_pack_11bit(raw, &frame[3]);
    frame[CRSF_RC_FRAME_SIZE - 1U] = crsf_crc8(&frame[2], 1U + RC_PACKED_BYTES);

    return CRSF_RC_FRAME_SIZE;
}

const char *crsf_status_text(crsf_status_t status)
{
    switch (status) {
    case CRSF_OK:          return "кадр прийнято";
    case CRSF_ERR_ARGS:    return "некоректні аргументи";
    case CRSF_ERR_SIZE:    return "кадр коротший за 26 байтів";
    case CRSF_ERR_ADDRESS: return "чужа адреса призначення";
    case CRSF_ERR_LENGTH:  return "невірне поле довжини";
    case CRSF_ERR_TYPE:    return "тип кадру не 0x16";
    case CRSF_ERR_CRC:     return "CRC8 не збігся";
    default:               return "невідомий стан";
    }
}
