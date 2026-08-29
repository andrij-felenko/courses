#include "frame_parser.h"

/* CRC-8, поліном 0x07, побітово. Саме заради таких циклів (вісім ітерацій
 * НА КОЖЕН байт) розбір і живе в нижній половині: на 168 МГц це дрібниця
 * для завдання й катастрофа для обробника, що спрацьовує щодесять мікросекунд. */
static uint8_t crc8_update(uint8_t crc, uint8_t byte)
{
    crc ^= byte;
    for (uint8_t bit = 0u; bit < 8u; bit++) {
        crc = (crc & 0x80u) ? (uint8_t)((crc << 1) ^ 0x07u) : (uint8_t)(crc << 1);
    }
    return crc;
}

void frame_parser_init(frame_parser_t *p)
{
    p->state = FRAME_WAIT_SOF;
    p->expected = 0u;
    p->filled = 0u;
    p->crc = 0u;
    p->frames_ok = 0u;
    p->crc_errors = 0u;
    p->length_errors = 0u;
}

bool frame_parser_feed(frame_parser_t *p, uint8_t byte, uint8_t *out_len)
{
    switch (p->state) {
    case FRAME_WAIT_SOF:
        /* Сміття до стартового байта мовчки викидаємо: після переповнення
         * кільця ми свідомо загубили байти, і потік майже напевно рваний. */
        if (byte == FRAME_SOF) {
            p->state = FRAME_WAIT_LEN;
            p->crc = 0u;
        }
        break;

    case FRAME_WAIT_LEN:
        if (byte == 0u || byte > FRAME_MAX_PAYLOAD) {
            /* Довжина поза контрактом — кадр биткий. Не «підлаштовуємось»
             * і не обрізаємо: повертаємось до пошуку стартового байта. */
            p->length_errors++;
            p->state = FRAME_WAIT_SOF;
            break;
        }
        p->expected = byte;
        p->filled = 0u;
        p->crc = crc8_update(p->crc, byte);
        p->state = FRAME_WAIT_BODY;
        break;

    case FRAME_WAIT_BODY:
        p->payload[p->filled++] = byte;
        p->crc = crc8_update(p->crc, byte);
        if (p->filled == p->expected) {
            p->state = FRAME_WAIT_CRC;
        }
        break;

    case FRAME_WAIT_CRC:
        p->state = FRAME_WAIT_SOF;
        if (byte == p->crc) {
            p->frames_ok++;
            *out_len = p->expected;
            return true;
        }
        p->crc_errors++;
        break;

    default:
        p->state = FRAME_WAIT_SOF;
        break;
    }

    return false;
}
