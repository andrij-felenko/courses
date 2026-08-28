#include <stdbool.h>

#define MAVLINK_STX_V2   0xFDu
#define MAVLINK_V2_HDR   10u   /* 0xFD + дев'ять байтів заголовка */

/* Чи цілий отриманий кадр. crc_extra беруть із згенерованої таблиці за визначником. */
bool frame_ok(const uint8_t *frame, uint8_t payload_len, uint8_t crc_extra)
{
    uint16_t crc = CRC_INIT;

    /* усе, крім початкового байта: заголовок і корисні дані */
    for (size_t i = 1; i < MAVLINK_V2_HDR + (size_t)payload_len; i++)
        crc_accumulate(frame[i], &crc);

    crc_accumulate(crc_extra, &crc);       /* ← відбиток опису домішується останнім */

    const uint8_t *tail = frame + MAVLINK_V2_HDR + payload_len;
    uint16_t received = (uint16_t)tail[0] | (uint16_t)((uint16_t)tail[1] << 8);
    return received == crc;
}
