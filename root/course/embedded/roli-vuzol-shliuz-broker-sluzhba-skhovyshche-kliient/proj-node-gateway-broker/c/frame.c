#include "frame.h"

#include <string.h>

uint16_t crc16_ccitt(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (int bit = 0; bit < 8; bit++) {
            crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

/* CRC рахуємо по БАЙТАХ дроту, а не по полях структури: так навіть якщо
   компілятор колись підсуне заповнювач, контрольна сума лишиться тією самою. */
static void seal(uint8_t out[FRAME_SIZE])
{
    uint16_t crc = crc16_ccitt(out, FRAME_SIZE - sizeof(uint16_t));
    memcpy(out + FRAME_SIZE - sizeof(uint16_t), &crc, sizeof crc);
}

void frame_build_telemetry(uint8_t out[FRAME_SIZE], uint16_t node_id, uint32_t seq,
                           int16_t temp_c100, uint16_t battery_mv, uint8_t flags)
{
    telemetry_frame_t f;
    memset(&f, 0, sizeof f);

    f.head.magic   = FRAME_MAGIC;
    f.head.type    = FRAME_TYPE_TELEMETRY;
    f.head.node_id = node_id;
    f.head.seq     = seq;
    f.temp_c100    = temp_c100;
    f.battery_mv   = battery_mv;
    f.flags        = flags;
    f.reserved     = 0x00;

    memcpy(out, &f, FRAME_SIZE);
    seal(out);
}

void frame_build_ack(uint8_t out[FRAME_SIZE], uint16_t node_id, uint32_t seq,
                     uint8_t cmd_id, uint8_t status, uint8_t flags)
{
    ack_frame_t f;
    memset(&f, 0, sizeof f);

    f.head.magic   = FRAME_MAGIC;
    f.head.type    = FRAME_TYPE_ACK;
    f.head.node_id = node_id;
    f.head.seq     = seq;          /* луна номера команди — за ним шлюз зіставляє квитанцію */
    f.cmd_id       = cmd_id;
    f.status       = status;
    f.flags        = flags;

    memcpy(out, &f, FRAME_SIZE);
    seal(out);
}

bool frame_valid(const uint8_t buf[FRAME_SIZE])
{
    if (buf[0] != FRAME_MAGIC) {
        return false;
    }

    uint16_t rx = 0;
    /* memcpy, а не *(uint16_t*)(buf + 14): на Cortex-M0 приведення вказівника
       до непарної адреси дає HardFault, а не число. */
    memcpy(&rx, buf + FRAME_SIZE - sizeof(uint16_t), sizeof rx);

    return rx == crc16_ccitt(buf, FRAME_SIZE - sizeof(uint16_t));
}

uint8_t frame_type_of(const uint8_t buf[FRAME_SIZE])
{
    return buf[1];
}

uint16_t frame_node_of(const uint8_t buf[FRAME_SIZE])
{
    uint16_t id = 0;
    memcpy(&id, buf + 2, sizeof id);
    return id;
}

bool frame_read_command(const uint8_t buf[FRAME_SIZE], command_frame_t *out)
{
    if (frame_type_of(buf) != FRAME_TYPE_COMMAND) {
        return false;
    }
    memcpy(out, buf, sizeof *out);
    return true;
}
