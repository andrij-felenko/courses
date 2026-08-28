/* test_geoid.c */
#include <assert.h>
#include <stdio.h>
#include "geoid.h"

#define NLAT 181u
#define NLON 360u

static uint8_t blob[GUN_HEADER_SIZE + NLAT * NLON * 2u];

static int16_t synth(uint32_t row, uint32_t col)
{
    return (int16_t)(2000 + 7 * (int32_t)row - 11 * (int32_t)col
                     + ((int32_t)row * (int32_t)col) / 3);
}

static void build(void)
{
    uint32_t row, col;
    uint8_t *p = blob;

    *p++ = 'G'; *p++ = 'U'; *p++ = 'N'; *p++ = '1';
    *p++ = (uint8_t)(NLAT & 0xFFu); *p++ = (uint8_t)(NLAT >> 8);
    *p++ = (uint8_t)(NLON & 0xFFu); *p++ = (uint8_t)(NLON >> 8);
    *p++ = 0; *p++ = 0;          /* flags = 0: рядок 0 — північний полюс */
    *p++ = 0; *p++ = 0;          /* reserved */

    for (row = 0; row < NLAT; ++row)
        for (col = 0; col < NLON; ++col) {
            uint16_t v = (uint16_t)synth(row, col);
            *p++ = (uint8_t)(v & 0xFFu);
            *p++ = (uint8_t)(v >> 8);
        }
}

int main(void)
{
    geoid_grid_t g;
    geoid_status_t st;

    build();
    st = geoid_open(&g, blob, sizeof blob);   /* поза assert: інакше під NDEBUG
                                                 сітка лишиться незавантаженою */
    assert(st == GEOID_OK);
    (void)st;
    assert(g.dlat_e7 == 10000000u && g.dlon_e7 == 10000000u);

    /* 50.25° пн. ш., 30.75° сх. д. — рівно три чверті комірки по обох осях */
    assert(geoid_undulation_cm(&g, 502500000, 307500000) == 2752);

    /* межа карти: сусід зі сходу — вузол 0 ТОГО САМОГО рядка */
    assert(geoid_undulation_cm(&g, 502500000, 1799000000) == 2360);

    /* +180.0000000° і −180.0000000° — той самий меридіан */
    assert(geoid_undulation_cm(&g, 502500000,  1800000000) ==
           geoid_undulation_cm(&g, 502500000, -1800000000));

    /* довгота поза [−180°, +180°) зводиться, а не ламає індекс */
    assert(geoid_undulation_cm(&g, 502500000,  2000000000) ==
           geoid_undulation_cm(&g, 502500000, -1600000000));

    /* полюси: беремо крайній рядок і не виходимо за масив */
    assert(geoid_undulation_cm(&g,  900000000, 0) == synth(0,   180));
    assert(geoid_undulation_cm(&g, -900000000, 0) == synth(180, 180));

    /* фікс: h = 245.300 м над еліпсоїдом → H над геоїдом */
    assert(geoid_amsl_mm(&g, 502500000, 307500000, 245300) == 217780);

    printf("ok\n");
    return 0;
}
