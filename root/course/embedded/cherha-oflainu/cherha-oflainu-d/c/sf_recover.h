/* Сканування кільця секторів на старті: де голова, де хвіст, який
 * наступний номер кадру. Покажчики у Flash не зберігаються взагалі —
 * їх відновлює цей прохід із самих кадрів. */
#ifndef SF_RECOVER_H
#define SF_RECOVER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Читання області черги. Повертає 0 при успіху, від'ємне при збої шини
 * SPI. Адреса — від початку виділеної під чергу області, не від початку
 * кристала: сканер не знає, де саме на носії лежить черга. */
typedef int (*sf_read_fn)(void *ctx, uint32_t addr, void *dst, size_t len);

typedef struct {
    sf_read_fn read;
    void      *ctx;
    uint32_t   sector_size;
    uint32_t   sector_count;
} sf_ring_t;

typedef struct {
    bool     empty;           /* жодного валідного кадру в кільці */
    uint32_t head_sector;     /* сектор, у який пишеться наступний кадр */
    uint32_t head_offset;     /* зсув у ньому: кінець останнього валідного */
    uint32_t next_seq;        /* номер, який отримає наступний кадр */
    uint32_t tail_sector;     /* найстаріший сектор із даними */
    uint32_t tail_seq;        /* номер найстарішого кадру в кільці */
    uint32_t valid_frames;    /* скільки кадрів пережило знеструмлення */
    uint32_t damaged_sectors; /* сектори, чий перший кадр не пройшов CRC */
    bool     torn_tail;       /* запис у голові обірвано на півдорозі */
} sf_state_t;

/* Повертає 0 при успіху, -1 при збої читання або хибних параметрах. */
int sf_recover(const sf_ring_t *ring, sf_state_t *out);

#endif /* SF_RECOVER_H */
