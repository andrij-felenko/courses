#ifndef GEO_H
#define GEO_H

/* Плоска (еквіпрямокутна) геометрія на масштабах місії до кількох десятків
   кілометрів. Похибка проти сфери тут менша за роздільність DEM, тому
   тригонометрії великого кола не заводимо. */

#define GEO_DEG_TO_RAD      0.017453292519943295
#define GEO_RAD_TO_DEG      57.29577951308232
#define GEO_METERS_PER_DEG  111320.0

typedef struct {
    double lat_deg;
    double lon_deg;
    float  alt_msl_m;   /* ортометрична висота над геоїдом EGM96 */
} GeoPoint;

float    geo_distance_m(GeoPoint a, GeoPoint b);
float    geo_bearing_deg(GeoPoint a, GeoPoint b);   /* азимут лінії шляху, 0 = північ */
GeoPoint geo_lerp(GeoPoint a, GeoPoint b, float t);
float    geo_wrap_deg(float deg);

#endif /* GEO_H */
