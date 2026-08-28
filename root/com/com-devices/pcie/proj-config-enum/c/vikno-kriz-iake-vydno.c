#include <stdint.h>
#include <stdio.h>

/* Початок вікна ECAM цього сегмента (з таблиці MCFG). */
static volatile uint8_t *ecam;

static inline volatile uint32_t *cfg_ptr(uint8_t bus, uint8_t dev, uint8_t fn, uint16_t off)
{
    return (volatile uint32_t *)(ecam + ((uint32_t)bus << 20)
                                      + ((uint32_t)dev << 15)
                                      + ((uint32_t)fn  << 12)
                                      + (off & ~3u));          /* вирівняно на слово */
}

static uint32_t cfg_r32(uint8_t b, uint8_t d, uint8_t f, uint16_t o)
{
    return *cfg_ptr(b, d, f, o);
}

static uint16_t cfg_r16(uint8_t b, uint8_t d, uint8_t f, uint16_t o)
{
    return (uint16_t)(cfg_r32(b, d, f, o) >> ((o & 2) * 8));
}

static uint8_t cfg_r8(uint8_t b, uint8_t d, uint8_t f, uint16_t o)
{
    return (uint8_t)(cfg_r32(b, d, f, o) >> ((o & 3) * 8));
}
