#include "framing.h"

#include <string.h>

#include "cobs.h"
#include "crc16.h"

void framing_reader_init(framing_reader_t *r, framing_frame_fn on_frame, void *ctx) {
    memset(r, 0, sizeof(*r));
    r->on_frame = on_frame;
    r->ctx = ctx;
}

link_status_t framing_build(uint8_t seq, const uint8_t *payload, size_t len,
                            uint8_t *wire, size_t wire_cap, size_t *wire_len) {
    if (len > LINK_MAX_PAYLOAD) {
        return LINK_ERR_TOO_LONG;
    }
    if (wire == NULL || wire_len == NULL || wire_cap < 2U) {
        return LINK_ERR_NO_SPACE;
    }

    uint8_t frame[LINK_MAX_FRAME];
    frame[0] = seq;
    if (len > 0U) {
        memcpy(&frame[LINK_SEQ_SIZE], payload, len);
    }

    const size_t body_len = LINK_SEQ_SIZE + len;
    const uint16_t crc = crc16_ccitt(frame, body_len);
    frame[body_len]      = (uint8_t)(crc >> 8);
    frame[body_len + 1U] = (uint8_t)(crc & 0xFFU);

    size_t encoded = 0U;
    // Один байт місткості лишаємо під роздільник.
    if (!cobs_encode(frame, body_len + LINK_CRC_SIZE, wire, wire_cap - 1U, &encoded)) {
        return LINK_ERR_NO_SPACE;
    }
    wire[encoded++] = LINK_DELIMITER;

    *wire_len = encoded;
    return LINK_OK;
}

link_status_t framing_reader_feed_byte(framing_reader_t *r, uint8_t byte) {
    if (byte != LINK_DELIMITER) {
        if (r->raw_len >= sizeof(r->raw)) {
            // Кадр не закінчився там, де мав: далі все до наступного 0x00 — сміття.
            if (!r->desync) {
                r->desync = true;
                r->stats.overflow++;
            }
            return LINK_ERR_OVERFLOW;
        }
        r->raw[r->raw_len++] = byte;
        return LINK_PENDING;
    }

    // Прийшов роздільник — на цьому місці приймач завжди повертається у синхронізм.
    if (r->desync) {
        r->raw_len = 0U;
        r->desync = false;
        return LINK_ERR_OVERFLOW;
    }
    if (r->raw_len == 0U) {
        return LINK_PENDING;   // тиша в лінії або два роздільники поспіль
    }

    size_t frame_len = 0U;
    const bool decoded = cobs_decode(r->raw, r->raw_len,
                                     r->frame, sizeof(r->frame), &frame_len);
    r->raw_len = 0U;

    if (!decoded) {
        r->stats.cobs_err++;
        return LINK_ERR_COBS;
    }
    if (frame_len < (LINK_SEQ_SIZE + LINK_CRC_SIZE)) {
        r->stats.crc_err++;
        return LINK_ERR_SHORT_FRAME;
    }
    // Остача над блоком РАЗОМ із CRC мусить дорівнювати нулю.
    if (crc16_ccitt(r->frame, frame_len) != 0U) {
        r->stats.crc_err++;
        return LINK_ERR_CRC;
    }

    r->stats.frames++;
    if (r->on_frame != NULL) {
        r->on_frame(r->frame[0],
                    &r->frame[LINK_SEQ_SIZE],
                    frame_len - LINK_SEQ_SIZE - LINK_CRC_SIZE,
                    r->ctx);
    }
    return LINK_OK;
}

void framing_reader_feed(framing_reader_t *r, const uint8_t *bytes, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        (void)framing_reader_feed_byte(r, bytes[i]);
    }
}
