#include "crc8.h"

/* Один такт зсувного регістра.
   Старший біт виштовхується ліворуч; якщо він був одиницею — поліном
   «підставляється під ділене» і віднімається, а віднімання в GF(2) — це XOR. */
static uint8_t shift_once(uint8_t reg)
{
    if (reg & 0x80u) {
        return (uint8_t)((reg << 1) ^ CRC8_POLY);
    }
    return (uint8_t)(reg << 1);
}

uint8_t crc8_bitwise(const uint8_t *data, size_t len)
{
    uint8_t crc = (uint8_t)CRC8_INIT;
    size_t i;

    if (data == NULL) {
        return crc; /* порожній кадр: регістр лишається початковим */
    }
    for (i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b) {
            crc = shift_once(crc);
        }
    }
    return crc;
}

uint8_t crc8_byte_trace(uint8_t reg, uint8_t data, uint8_t steps[8])
{
    reg ^= data; /* змішування байта з поточним залишком */
    for (int b = 0; b < 8; ++b) {
        reg = shift_once(reg);
        if (steps != NULL) {
            steps[b] = reg;
        }
    }
    return reg;
}

void crc8_build_table(uint8_t table[256])
{
    if (table == NULL) {
        return;
    }
    for (unsigned i = 0; i < 256u; ++i) {
        uint8_t reg = (uint8_t)i;
        for (int b = 0; b < 8; ++b) {
            reg = shift_once(reg);
        }
        table[i] = reg;
    }
}

const uint8_t *crc8_table(void)
{
    static uint8_t table[256];
    static bool ready = false;

    if (!ready) {
        crc8_build_table(table);
        ready = true; /* на мікроконтролері таблиця зазвичай лежить у Flash як const */
    }
    return table;
}

uint8_t crc8_fast(const uint8_t *data, size_t len)
{
    const uint8_t *table = crc8_table();
    uint8_t crc = (uint8_t)CRC8_INIT;
    size_t i;

    if (data == NULL) {
        return crc;
    }
    for (i = 0; i < len; ++i) {
        crc = table[crc ^ data[i]];
    }
    return crc;
}

bool crc8_frame_ok(const uint8_t *frame, size_t len)
{
    if (frame == NULL || len < 2) {
        return false; /* нема ні даних, ні байта контрольної суми */
    }
    /* Байт CRC у кінці кадру гасить регістр: після нього залишок дорівнює нулю. */
    return crc8_fast(frame, len) == 0x00u;
}

int crc8_sht3x_word(const uint8_t *frame, size_t len, uint16_t *out)
{
    if (frame == NULL || out == NULL || len != 3) {
        return -1;
    }
    if (crc8_fast(frame, 2) != frame[2]) {
        return -1; /* контрольна сума не збіглася — слово віддавати не можна */
    }
    *out = (uint16_t)(((uint16_t)frame[0] << 8) | frame[1]);
    return 0;
}
