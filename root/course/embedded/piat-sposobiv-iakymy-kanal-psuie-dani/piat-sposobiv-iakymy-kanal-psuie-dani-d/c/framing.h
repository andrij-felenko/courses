#ifndef FRAMING_H
#define FRAMING_H

#include "link.h"

// Стадії 1–3 конвеєра приймача: демаркація меж по 0x00, COBS-декодування,
// контроль цілісності CRC-16. Нагору віддається лише кадр, що пройшов усі три.
typedef void (*framing_frame_fn)(uint8_t seq, const uint8_t *payload, size_t len, void *ctx);

typedef struct {
    uint8_t raw[LINK_MAX_WIRE];     // сирий шматок між двома роздільниками
    size_t  raw_len;
    uint8_t frame[LINK_MAX_FRAME];  // кадр після COBS-декодування
    bool    desync;                 // у лінії сміття: чекаємо наступного 0x00

    framing_frame_fn on_frame;
    void            *ctx;

    struct {
        uint32_t frames;    // кадрів, що пройшли CRC
        uint32_t cobs_err;  // структурно пошкоджених тіл
        uint32_t crc_err;   // кадрів, побитих шумом
        uint32_t overflow;  // випадків, коли роздільник так і не прийшов
    } stats;
} framing_reader_t;

void framing_reader_init(framing_reader_t *r, framing_frame_fn on_frame, void *ctx);

// Байти приходять із UART/DMA довільними шматками — і по одному, і пачками.
link_status_t framing_reader_feed_byte(framing_reader_t *r, uint8_t byte);
void framing_reader_feed(framing_reader_t *r, const uint8_t *bytes, size_t len);

// Пакування кадру для лінії: [seq][payload][CRC-16] -> COBS -> 0x00.
link_status_t framing_build(uint8_t seq, const uint8_t *payload, size_t len,
                            uint8_t *wire, size_t wire_cap, size_t *wire_len);

#endif // FRAMING_H
