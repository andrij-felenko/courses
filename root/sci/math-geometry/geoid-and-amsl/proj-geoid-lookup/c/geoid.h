/* geoid.h — ундуляція геоїда з готової сітки.
   Координати — degE7 (1e−7 градуса), як їх возить MAVLink.
   Результат — сантиметри. Жодної плаваючої коми. */
#ifndef GEOID_H
#define GEOID_H

#include <stdint.h>
#include <stddef.h>

#define GUN_HEADER_SIZE       12u
#define GUN_FLAG_SOUTH_FIRST  0x0001u

typedef struct {
    const uint8_t *node;   /* перший байт масиву значень, сирий int16 LE */
    uint32_t nlat;         /* вузлів по широті, разом з обома полюсами   */
    uint32_t nlon;         /* вузлів по довготі, БЕЗ дубля +180°         */
    uint32_t dlat_e7;      /* крок по широті,  degE7                     */
    uint32_t dlon_e7;      /* крок по довготі, degE7                     */
    uint32_t flags;
} geoid_grid_t;

typedef enum {
    GEOID_OK = 0,
    GEOID_ERR_MAGIC,
    GEOID_ERR_SIZE,
    GEOID_ERR_STEP
} geoid_status_t;

geoid_status_t geoid_open(geoid_grid_t *g, const uint8_t *blob, size_t len);
int32_t geoid_undulation_cm(const geoid_grid_t *g, int32_t lat_e7, int32_t lon_e7);
int32_t geoid_amsl_mm(const geoid_grid_t *g, int32_t lat_e7, int32_t lon_e7, int32_t h_mm);
int32_t geoid_ellipsoid_mm(const geoid_grid_t *g, int32_t lat_e7, int32_t lon_e7, int32_t amsl_mm);

#endif /* GEOID_H */


/* ── geoid.c ──────────────────────────────────────────────────────────── */
#include "geoid.h"

static uint32_t rd16(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8);
}

geoid_status_t geoid_open(geoid_grid_t *g, const uint8_t *blob, size_t len)
{
    uint32_t nlat, nlon, dlat, dlon;

    if (len < GUN_HEADER_SIZE)
        return GEOID_ERR_SIZE;
    if (blob[0] != 'G' || blob[1] != 'U' || blob[2] != 'N' || blob[3] != '1')
        return GEOID_ERR_MAGIC;

    nlat = rd16(blob + 4);
    nlon = rd16(blob + 6);
    if (nlat < 2u || nlon < 2u)
        return GEOID_ERR_SIZE;
    /* файл мусить містити рівно nlat·nlon значень по два байти — не менше
       (обрізали при заливці) і не більше (склеїли два файли) */
    if (len - GUN_HEADER_SIZE != (size_t)nlat * nlon * 2u)
        return GEOID_ERR_SIZE;

    /* сітка глобальна: рядки покривають 180°, стовпці — 360°.
       Крок не читаємо з файлу — виводимо, тож розійтися з nlat/nlon нема з чим. */
    dlat = 1800000000u / (nlat - 1u);
    dlon = 3600000000u / nlon;
    if (dlat * (nlat - 1u) != 1800000000u)   /* крок не цілий у degE7 */
        return GEOID_ERR_STEP;
    if (dlon * nlon != 3600000000u)
        return GEOID_ERR_STEP;
    /* нижче буде (rem << 8), а rem < крок: щоб зсув лишився в 32 бітах,
       крок мусить бути менший за 2²⁴ — тобто сітка не грубіша за 1.67° */
    if (dlat > 0xFFFFFFu || dlon > 0xFFFFFFu)
        return GEOID_ERR_STEP;

    g->node    = blob + GUN_HEADER_SIZE;
    g->nlat    = nlat;
    g->nlon    = nlon;
    g->dlat_e7 = dlat;
    g->dlon_e7 = dlon;
    g->flags   = rd16(blob + 8);
    return GEOID_OK;
}

static int32_t node_cm(const geoid_grid_t *g, uint32_t row, uint32_t col)
{
    /* значення лежать сирими int16 little-endian: збираємо їх з байтів,
       щоб не залежати ні від вирівнювання адреси, ні від порядку байтів ЦП */
    const uint8_t *p = g->node + ((size_t)row * g->nlon + col) * 2u;
    return (int16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

int32_t geoid_undulation_cm(const geoid_grid_t *g, int32_t lat_e7, int32_t lon_e7)
{
    uint32_t t, u, rem, r0, r1, c0, c1, fx, fy;
    int32_t  n00, n01, n10, n11, top, bot, val;
    int64_t  l;

    /* --- широта: t росте разом з індексом рядка, хай там який напрям --- */
    if (lat_e7 >  900000000) lat_e7 =  900000000;
    if (lat_e7 < -900000000) lat_e7 = -900000000;
    t = (g->flags & GUN_FLAG_SOUTH_FIRST)
      ? (uint32_t)(lat_e7 + 900000000)     /* рядок 0 — південний полюс */
      : (uint32_t)(900000000 - lat_e7);    /* рядок 0 — північний полюс */

    r0  = t / g->dlat_e7;
    rem = t - r0 * g->dlat_e7;
    fy  = (rem << 8) / g->dlat_e7;
    if (r0 >= g->nlat - 1u) {              /* точно на дальньому полюсі */
        r0 = g->nlat - 2u;
        fy = 256u;
    }
    r1 = r0 + 1u;

    /* --- довгота: зводимо до [−180°, +180°) і рахуємо на схід від −180° --- */
    l = (int64_t)lon_e7 + 1800000000;
    l %= 3600000000LL;
    if (l < 0) l += 3600000000LL;
    u = (uint32_t)l;

    c0  = u / g->dlon_e7;
    rem = u - c0 * g->dlon_e7;
    fx  = (rem << 8) / g->dlon_e7;
    c1  = c0 + 1u;
    if (c1 == g->nlon) c1 = 0u;            /* замикання меридіана */

    /* --- білінійна інтерполяція, Q8 → Q16 --- */
    n00 = node_cm(g, r0, c0);  n01 = node_cm(g, r0, c1);
    n10 = node_cm(g, r1, c0);  n11 = node_cm(g, r1, c1);

    top = n00 * (int32_t)(256u - fx) + n01 * (int32_t)fx;
    bot = n10 * (int32_t)(256u - fx) + n11 * (int32_t)fx;
    val = top * (int32_t)(256u - fy) + bot * (int32_t)fy;

    return (val + 32768) >> 16;
}

/* h = H + N. Висоти — у міліметрах, як у MAVLink; ундуляція — у сантиметрах. */
int32_t geoid_amsl_mm(const geoid_grid_t *g, int32_t lat_e7, int32_t lon_e7, int32_t h_mm)
{
    return h_mm - geoid_undulation_cm(g, lat_e7, lon_e7) * 10;
}

int32_t geoid_ellipsoid_mm(const geoid_grid_t *g, int32_t lat_e7, int32_t lon_e7, int32_t amsl_mm)
{
    return amsl_mm + geoid_undulation_cm(g, lat_e7, lon_e7) * 10;
}
