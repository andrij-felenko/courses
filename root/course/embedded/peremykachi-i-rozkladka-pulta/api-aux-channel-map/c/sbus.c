#include "sbus.h"

#include <string.h>

sbus_status_t sbus_parse(const uint8_t *frame, size_t len, sbus_frame_t *out)
{
    if (frame == NULL || out == NULL) {
        return SBUS_ERR_ARGS;
    }
    if (len < SBUS_FRAME_SIZE) {
        return SBUS_ERR_SIZE;
    }
    if (frame[0] != SBUS_HEADER) {
        return SBUS_ERR_HEADER;
    }
    if (frame[SBUS_FRAME_SIZE - 1U] != SBUS_FOOTER &&
        frame[SBUS_FRAME_SIZE - 1U] != SBUS_FOOTER_V2) {
        return SBUS_ERR_FOOTER;
    }

    memset(out, 0, sizeof(*out));
    rc_unpack_11bit(&frame[1], out->raw);

    const uint8_t flags = frame[23];
    out->ch17       = (flags & SBUS_FLAG_CH17) != 0U;
    out->ch18       = (flags & SBUS_FLAG_CH18) != 0U;
    out->frame_lost = (flags & SBUS_FLAG_FRAME_LOST) != 0U;
    out->failsafe   = (flags & SBUS_FLAG_FAILSAFE) != 0U;

    return SBUS_OK;
}

size_t sbus_build(const sbus_frame_t *in, uint8_t frame[SBUS_FRAME_SIZE])
{
    if (in == NULL || frame == NULL) {
        return 0U;
    }

    frame[0] = SBUS_HEADER;
    rc_pack_11bit(in->raw, &frame[1]);

    uint8_t flags = 0U;
    if (in->ch17)       { flags |= SBUS_FLAG_CH17; }
    if (in->ch18)       { flags |= SBUS_FLAG_CH18; }
    if (in->frame_lost) { flags |= SBUS_FLAG_FRAME_LOST; }
    if (in->failsafe)   { flags |= SBUS_FLAG_FAILSAFE; }

    frame[23] = flags;
    frame[24] = SBUS_FOOTER;
    return SBUS_FRAME_SIZE;
}

const char *sbus_status_text(sbus_status_t status)
{
    switch (status) {
    case SBUS_OK:         return "кадр прийнято";
    case SBUS_ERR_ARGS:   return "некоректні аргументи";
    case SBUS_ERR_SIZE:   return "кадр коротший за 25 байтів";
    case SBUS_ERR_HEADER: return "стартовий байт не 0x0F";
    case SBUS_ERR_FOOTER: return "неприпустимий стоповий байт";
    default:              return "невідомий стан";
    }
}
