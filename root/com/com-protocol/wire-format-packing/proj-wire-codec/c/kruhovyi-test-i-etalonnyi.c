#include <stdio.h>

static const uint8_t TELEM_REF[TELEM_SIZE] = {
    0xA5,0xC3, 0x01, 0x05, 0x00,0x20, 0x00,0x00,
    0x00,0x04,0x62,0xD5,0x3C,0x8A,0xBA,0xC0,
    0x1E,0x12,0x13,0x08,
    0x12,0x31,0x88,0x20,
    0xFF,0xFF,0xFB,0x1E,
    0x2E,0x42,
    0x03,0x87
};

int main(void)
{
    /* 0. Сама сума — за контрольним рядком каталогу. */
    if (crc16((const uint8_t *)"123456789", 9) != 0x29B1) return 1;

    const telem_t t = {
        .time_us = UINT64_C(1234567890123456),
        .lat_e7  =  504501000,   /* 50.4501° пн. ш. */
        .lon_e7  =  305236000,   /* 30.5236° сх. д. */
        .alt_mm  =      -1250,   /* 1.25 м НИЖЧЕ точки зльоту */
        .mv      =      11842,
        .flags   =       0x05
    };

    uint8_t buf[64];
    /* 1. Байт у байт із еталоном. */
    if (telem_encode(buf, sizeof buf, &t) != TELEM_SIZE)  return 2;
    if (memcmp(buf, TELEM_REF, TELEM_SIZE) != 0)          return 3;

    /* 2. Коло: розібране дорівнює зібраному. */
    telem_t back;
    if (telem_decode(buf, TELEM_SIZE, &back) != TELEM_OK) return 4;
    if (back.time_us != t.time_us || back.lat_e7 != t.lat_e7 ||
        back.lon_e7  != t.lon_e7  || back.alt_mm != t.alt_mm ||
        back.mv      != t.mv      || back.flags  != t.flags)  return 5;

    /* 3. Будь-який обрізок — відмова, а не падіння. */
    for (size_t k = 0; k < TELEM_SIZE; k++)
        if (telem_decode(buf, k, &back) == TELEM_OK)       return 6;

    /* 4. Один перекинутий біт у будь-якому місці — спіймано. */
    for (size_t i = 0; i < TELEM_SIZE; i++)
        for (int b = 0; b < 8; b++) {
            uint8_t spoiled[TELEM_SIZE];
            memcpy(spoiled, buf, TELEM_SIZE);
            spoiled[i] ^= (uint8_t)(1u << b);
            if (telem_decode(spoiled, TELEM_SIZE, &back) == TELEM_OK) return 7;
        }

    /* 5. Затісний буфер — нуль і жодного запису за межу. */
    uint8_t tiny[TELEM_SIZE - 1];
    if (telem_encode(tiny, sizeof tiny, &t) != 0)         return 8;

    puts("codec ok");
    return 0;
}
