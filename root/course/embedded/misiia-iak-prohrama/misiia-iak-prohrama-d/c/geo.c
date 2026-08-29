#include "geo.h"

#include <math.h>

#define DEG_E7         1.0e-7f
#define M_PER_DEG_LAT  111320.0f
#define DEG2RAD        0.01745329252f

static float lat_deg(int32_t lat_e7)
{
    return (float)lat_e7 * DEG_E7;
}

geo_offset_t geo_offset(geo_point_t from, geo_point_t to)
{
    /* Різницю беремо в цілих і лише потім масштабуємо. Різниця сотень
       метрів у одиницях 1e-7° — це десятки тисяч, для float це точно. */
    const float d_lat_deg = (float)(to.lat_e7 - from.lat_e7) * DEG_E7;
    const float d_lon_deg = (float)(to.lon_e7 - from.lon_e7) * DEG_E7;

    /* Меридіани сходяться до полюсів: довжина градуса довготи
       множиться на косинус широти. */
    const float k_lon = cosf(lat_deg(from.lat_e7) * DEG2RAD);

    geo_offset_t o;
    o.north_m = d_lat_deg * M_PER_DEG_LAT;
    o.east_m  = d_lon_deg * M_PER_DEG_LAT * k_lon;
    return o;
}

float geo_dist_sq_m2(geo_point_t a, geo_point_t b)
{
    const geo_offset_t o = geo_offset(a, b);
    return o.east_m * o.east_m + o.north_m * o.north_m;
}

float geo_bearing_deg(geo_point_t from, geo_point_t to)
{
    const geo_offset_t o = geo_offset(from, to);
    if (o.east_m == 0.0f && o.north_m == 0.0f) {
        return 0.0f;
    }
    /* atan2(схід, північ) — курс від півночі за годинниковою стрілкою. */
    return geo_norm_heading_deg(atan2f(o.east_m, o.north_m) / DEG2RAD);
}

float geo_wrap_deg(float angle_deg)
{
    float a = fmodf(angle_deg + 180.0f, 360.0f);
    if (a < 0.0f) {
        a += 360.0f;
    }
    return a - 180.0f;
}

float geo_norm_heading_deg(float angle_deg)
{
    float a = fmodf(angle_deg, 360.0f);
    if (a < 0.0f) {
        a += 360.0f;
    }
    return a;
}

geo_point_t geo_shift(geo_point_t base, float east_m, float north_m)
{
    const float k_lon = cosf(lat_deg(base.lat_e7) * DEG2RAD);

    geo_point_t p = base;
    p.lat_e7 += (int32_t)lrintf(north_m / M_PER_DEG_LAT / DEG_E7);
    if (fabsf(k_lon) > 1.0e-6f) {
        p.lon_e7 += (int32_t)lrintf(east_m / (M_PER_DEG_LAT * k_lon) / DEG_E7);
    }
    return p;
}
