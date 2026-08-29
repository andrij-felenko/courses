#ifndef DSHOT_H
#define DSHOT_H

#include <stdbool.h>
#include <stdint.h>

/* DShot: 11-бітне значення тяги. 0 — команда «стоп», робочий діапазон 48..2047. */
static inline uint16_t dshot_throttle_value(float u, bool armed)
{
    if (!armed || !(u > 0.0f)) return 0;   /* NaN теж потрапляє сюди — і це правильно */
    if (u > 1.0f) u = 1.0f;
    return (uint16_t)(48.0f + u * (2047.0f - 48.0f) + 0.5f);
}

/* Кадр: 11 біт значення, біт запиту телеметрії, CRC4 по цих дванадцяти. */
static inline uint16_t dshot_packet(uint16_t value, bool telemetry)
{
    const uint16_t v = (uint16_t)(((value & 0x7FFu) << 1) | (telemetry ? 1u : 0u));
    const uint16_t crc = (uint16_t)((v ^ (v >> 4) ^ (v >> 8)) & 0x0Fu);
    return (uint16_t)((v << 4) | crc);
}

#endif /* DSHOT_H */
