#include "geo.h"

#include <math.h>

float geo_wrap_deg(float deg)
{
    if (!isfinite(deg)) {
        return 0.0f;
    }
    deg = fmodf(deg, 360.0f);
    if (deg < 0.0f) {
        deg += 360.0f;
    }
    return deg;
}

/* Зміщення в метрах: north — уздовж меридіана, east — уздовж паралелі
   на середній широті відрізка. */
static void geo_offsets_m(GeoPoint a, GeoPoint b, double *east_m, double *north_m)
{
    const double mid_lat_rad = 0.5 * (a.lat_deg + b.lat_deg) * GEO_DEG_TO_RAD;

    *north_m = (b.lat_deg - a.lat_deg) * GEO_METERS_PER_DEG;
    *east_m  = (b.lon_deg - a.lon_deg) * GEO_METERS_PER_DEG * cos(mid_lat_rad);
}

float geo_distance_m(GeoPoint a, GeoPoint b)
{
    double east, north;
    geo_offsets_m(a, b, &east, &north);
    return (float)sqrt(east * east + north * north);
}

float geo_bearing_deg(GeoPoint a, GeoPoint b)
{
    double east, north;
    geo_offsets_m(a, b, &east, &north);

    /* Вироджений відрізок: азимут не визначений, віддаємо 0 —
       валідатор такий відрізок відсіює окремою перевіркою довжини. */
    if (east == 0.0 && north == 0.0) {
        return 0.0f;
    }
    return geo_wrap_deg((float)(atan2(east, north) * GEO_RAD_TO_DEG));
}

GeoPoint geo_lerp(GeoPoint a, GeoPoint b, float t)
{
    GeoPoint p;
    p.lat_deg   = a.lat_deg + (b.lat_deg - a.lat_deg) * (double)t;
    p.lon_deg   = a.lon_deg + (b.lon_deg - a.lon_deg) * (double)t;
    p.alt_msl_m = a.alt_msl_m + (b.alt_msl_m - a.alt_msl_m) * t;
    return p;
}
