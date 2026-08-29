#include "packet.h"

#include <string.h>

#include "crc16.h"
#include "whitening.h"

size_t packet_build(const uint8_t *payload, uint8_t len,
                    uint8_t *frame_out, size_t frame_cap)
{
    if (payload == NULL || frame_out == NULL) {
        return 0;
    }
    if (len == 0 || len > PACKET_MAX_PAYLOAD) {
        return 0;
    }

    const size_t need = PREAMBLE_LEN + 2 + 1 + (size_t)len + 2;
    if (frame_cap < need) {
        return 0;
    }

    size_t idx = 0;

    /* 1. Преамбула. Її не скремблюють: приймач саме за нею ловить фазу біта,
          тож вона мусить лишитися рівним чергуванням 0 і 1. */
    memset(frame_out, PREAMBLE_BYTE, PREAMBLE_LEN);
    idx += PREAMBLE_LEN;

    /* 2. Синхрослово теж іде як є — корелятор шукає точний бітовий візерунок. */
    frame_out[idx++] = (uint8_t)(SYNC_WORD >> 8);
    frame_out[idx++] = (uint8_t)(SYNC_WORD & 0xFFu);

    /* 3. Тіло кадру: байт довжини й корисні дані. */
    const size_t body = idx;
    frame_out[idx++] = len;
    memcpy(&frame_out[idx], payload, len);
    idx += len;

    /* 4. CRC рахуємо ДО скремблювання, по чистому тілу: так само робить
          апаратний блок трансивера, і так само його перевірить приймач. */
    const uint16_t crc = crc16_block(&frame_out[body], (size_t)len + 1u);
    frame_out[idx++] = (uint8_t)(crc >> 8);
    frame_out[idx++] = (uint8_t)(crc & 0xFFu);

    /* 5. Скремблюємо все тіло разом із контрольною сумою одним потоком LFSR —
          інакше довгий хвіст нулів у даних лишив би передавач на одній частоті. */
    whitening_block(&frame_out[body], idx - body);

    return idx;
}
