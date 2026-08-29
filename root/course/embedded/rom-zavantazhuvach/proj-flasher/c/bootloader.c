#include "bootloader.h"

#define ACK_BYTE  0x79
#define NACK_BYTE 0x1F

#define CMD_SYNC      0x7F
#define CMD_GET_VER   0x01
#define CMD_GET_ID    0x02
#define CMD_READ      0x11
#define CMD_GO        0x21
#define CMD_WRITE     0x31
#define CMD_ERASE_EXT 0x44
#define CMD_UNPROTECT 0x92

#define ACK_TIMEOUT_MS    1000u
#define SYNC_TIMEOUT_MS   2000u
#define WRITE_TIMEOUT_MS  3000u
#define ERASE_TIMEOUT_MS 30000u /* високовольтне стирання всієї матриці — довго */

const char *bl_status_text(bl_status status)
{
    switch (status) {
    case BL_OK:           return "успіх";
    case BL_ERR_IO:       return "збій запису або читання порту";
    case BL_ERR_TIMEOUT:  return "завантажувач не відповів";
    case BL_ERR_NACK:     return "чип відповів NACK";
    case BL_ERR_PROTOCOL: return "неочікуваний байт у відповіді";
    case BL_ERR_ARG:      return "хибний аргумент";
    }
    return "невідома помилка";
}

static bl_status wait_ack(const serial_port *port, unsigned timeout_ms)
{
    uint8_t b = 0;
    if (!serial_read_exact(port, &b, 1, timeout_ms)) {
        return BL_ERR_TIMEOUT;
    }
    if (b == ACK_BYTE) {
        return BL_OK;
    }
    if (b == NACK_BYTE) {
        return BL_ERR_NACK;
    }
    return BL_ERR_PROTOCOL;
}

/* Кожна команда — байт коду і його побітова інверсія. */
static bl_status send_command(const serial_port *port, uint8_t code, unsigned timeout_ms)
{
    const uint8_t frame[2] = {code, (uint8_t)~code};
    if (!serial_write_all(port, frame, sizeof frame)) {
        return BL_ERR_IO;
    }
    return wait_ack(port, timeout_ms);
}

/* Адреса — 4 байти зі старшого, п'ятий байт: XOR попередніх чотирьох. */
static bl_status send_address(const serial_port *port, uint32_t address)
{
    uint8_t frame[5];
    frame[0] = (uint8_t)(address >> 24);
    frame[1] = (uint8_t)(address >> 16);
    frame[2] = (uint8_t)(address >> 8);
    frame[3] = (uint8_t)address;
    frame[4] = (uint8_t)(frame[0] ^ frame[1] ^ frame[2] ^ frame[3]);

    if (!serial_write_all(port, frame, sizeof frame)) {
        return BL_ERR_IO;
    }
    return wait_ack(port, ACK_TIMEOUT_MS);
}

bl_status bl_sync(const serial_port *port)
{
    const uint8_t sync = CMD_SYNC;

    /* Під час скидання ніжки в Hi-Z, і лінія RX могла зловити фальшивий стартовий
       біт. Усе, що встигло прийти до синхронізації, викидаємо. */
    serial_flush(port);

    if (!serial_write_all(port, &sync, 1)) {
        return BL_ERR_IO;
    }
    return wait_ack(port, SYNC_TIMEOUT_MS);
}

bl_status bl_get_version(const serial_port *port, uint8_t *version, uint8_t option_bytes[2])
{
    bl_status st = send_command(port, CMD_GET_VER, ACK_TIMEOUT_MS);
    if (st != BL_OK) {
        return st;
    }

    uint8_t reply[3];
    if (!serial_read_exact(port, reply, sizeof reply, ACK_TIMEOUT_MS)) {
        return BL_ERR_TIMEOUT;
    }

    st = wait_ack(port, ACK_TIMEOUT_MS);
    if (st != BL_OK) {
        return st;
    }

    *version = reply[0];
    option_bytes[0] = reply[1];
    option_bytes[1] = reply[2];
    return BL_OK;
}

bl_status bl_get_id(const serial_port *port, uint16_t *pid)
{
    bl_status st = send_command(port, CMD_GET_ID, ACK_TIMEOUT_MS);
    if (st != BL_OK) {
        return st;
    }

    uint8_t n = 0;
    if (!serial_read_exact(port, &n, 1, ACK_TIMEOUT_MS)) {
        return BL_ERR_TIMEOUT;
    }
    if (n != 1) {
        return BL_ERR_PROTOCOL; /* очікуємо рівно два байти PID, тобто N = 1 */
    }

    uint8_t id_bytes[2];
    if (!serial_read_exact(port, id_bytes, sizeof id_bytes, ACK_TIMEOUT_MS)) {
        return BL_ERR_TIMEOUT;
    }

    st = wait_ack(port, ACK_TIMEOUT_MS);
    if (st != BL_OK) {
        return st;
    }

    *pid = (uint16_t)(((uint16_t)id_bytes[0] << 8) | id_bytes[1]);
    return BL_OK;
}

bl_status bl_readout_unprotect(const serial_port *port)
{
    bl_status st = send_command(port, CMD_UNPROTECT, ACK_TIMEOUT_MS);
    if (st != BL_OK) {
        return st;
    }
    /* Другий ACK приходить після того, як чип сам стер усю Flash. Далі він
       перезавантажується, тож викликач мусить наново зайти в завантажувач. */
    return wait_ack(port, ERASE_TIMEOUT_MS);
}

bl_status bl_mass_erase(const serial_port *port)
{
    bl_status st = send_command(port, CMD_ERASE_EXT, ACK_TIMEOUT_MS);
    if (st != BL_OK) {
        return st;
    }

    /* Спецкод 0xFFFF означає «стерти все», контрольна сума 0xFF ^ 0xFF = 0x00 */
    const uint8_t params[3] = {0xFF, 0xFF, 0x00};
    if (!serial_write_all(port, params, sizeof params)) {
        return BL_ERR_IO;
    }
    return wait_ack(port, ERASE_TIMEOUT_MS);
}

bl_status bl_write_block(const serial_port *port, uint32_t address, const uint8_t *data, size_t len)
{
    if (len == 0 || len > BL_MAX_BLOCK) {
        return BL_ERR_ARG;
    }

    bl_status st = send_command(port, CMD_WRITE, ACK_TIMEOUT_MS);
    if (st != BL_OK) {
        return st;
    }

    st = send_address(port, address);
    if (st != BL_OK) {
        return st;
    }

    /* N = len - 1, далі тіло, останній байт — XOR від N і всіх байтів даних */
    uint8_t payload[BL_MAX_BLOCK + 2];
    uint8_t n = (uint8_t)(len - 1);
    uint8_t checksum = n;

    payload[0] = n;
    for (size_t i = 0; i < len; ++i) {
        payload[1 + i] = data[i];
        checksum ^= data[i];
    }
    payload[1 + len] = checksum;

    if (!serial_write_all(port, payload, len + 2)) {
        return BL_ERR_IO;
    }
    return wait_ack(port, WRITE_TIMEOUT_MS);
}

bl_status bl_read_block(const serial_port *port, uint32_t address, uint8_t *buf, size_t len)
{
    if (len == 0 || len > BL_MAX_BLOCK) {
        return BL_ERR_ARG;
    }

    bl_status st = send_command(port, CMD_READ, ACK_TIMEOUT_MS);
    if (st != BL_OK) {
        return st; /* NACK тут — найчастіше RDP level 1 */
    }

    st = send_address(port, address);
    if (st != BL_OK) {
        return st;
    }

    /* Кількість байтів і її інверсія як контрольна сума */
    const uint8_t n = (uint8_t)(len - 1);
    const uint8_t frame[2] = {n, (uint8_t)~n};
    if (!serial_write_all(port, frame, sizeof frame)) {
        return BL_ERR_IO;
    }

    st = wait_ack(port, ACK_TIMEOUT_MS);
    if (st != BL_OK) {
        return st;
    }

    if (!serial_read_exact(port, buf, len, WRITE_TIMEOUT_MS)) {
        return BL_ERR_TIMEOUT;
    }
    return BL_OK;
}

bl_status bl_go(const serial_port *port, uint32_t address)
{
    bl_status st = send_command(port, CMD_GO, ACK_TIMEOUT_MS);
    if (st != BL_OK) {
        return st;
    }
    return send_address(port, address);
}
