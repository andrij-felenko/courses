// geofence_engine.c — Виробничий модуль геозонування на C99 для польотних контролерів.
// Без динамічного виділення пам'яті (Zero-Heap Allocation).

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_POLY_VERTICES 16
#define MAX_POLYGONS     8
#define MAX_CYLINDERS    8

typedef struct {
    int32_t lat_e7;
    int32_t lon_e7;
    float   alt_m;
} GeoPoint;

typedef struct {
    int32_t min_lat;
    int32_t max_lat;
    int32_t min_lon;
    int32_t max_lon;
} BoundingBoxAABB;

typedef struct {
    GeoPoint       vertices[MAX_POLY_VERTICES];
    uint8_t        count;
    bool           is_keep_in;
    float          alt_min;
    float          alt_max;
    BoundingBoxAABB aabb;
    bool           active;
} PolygonFence;

typedef struct {
    GeoPoint center;
    float    radius_m;
    float    alt_min;
    float    alt_max;
    bool     is_keep_in;
    bool     active;
} CylinderFence;

typedef struct {
    PolygonFence  polygons[MAX_POLYGONS];
    CylinderFence cylinders[MAX_CYLINDERS];
    uint8_t       poly_count;
    uint8_t       cyl_count;
    float         max_braking_accel; // м/с²
    float         latency_sec;       // с
    float         static_margin_m;   // м
} GeofenceEngine;

// Оновлення AABB габаритів полігона
static void update_polygon_aabb(PolygonFence *poly) {
    if (poly->count == 0) return;
    poly->aabb.min_lat = poly->vertices[0].lat_e7;
    poly->aabb.max_lat = poly->vertices[0].lat_e7;
    poly->aabb.min_lon = poly->vertices[0].lon_e7;
    poly->aabb.max_lon = poly->vertices[0].lon_e7;

    for (uint8_t i = 1; i < poly->count; i++) {
        if (poly->vertices[i].lat_e7 < poly->aabb.min_lat) poly->aabb.min_lat = poly->vertices[i].lat_e7;
        if (poly->vertices[i].lat_e7 > poly->aabb.max_lat) poly->aabb.max_lat = poly->vertices[i].lat_e7;
        if (poly->vertices[i].lon_e7 < poly->aabb.min_lon) poly->aabb.min_lon = poly->vertices[i].lon_e7;
        if (poly->vertices[i].lon_e7 > poly->aabb.max_lon) poly->aabb.max_lon = poly->vertices[i].lon_e7;
    }
}

// Цілочисельний Ray-Casting
static bool is_point_in_polygon_fast(int32_t lat, int32_t lon, const PolygonFence *poly) {
    // Рівень 1: AABB фільтр O(1)
    if (lat < poly->aabb.min_lat || lat > poly->aabb.max_lat ||
        lon < poly->aabb.min_lon || lon > poly->aabb.max_lon) {
        return false;
    }

    // Рівень 2: Перевірка перетинів ребер O(N)
    bool inside = false;
    uint8_t j = poly->count - 1;

    for (uint8_t i = 0; i < poly->count; i++) {
        int32_t yi = poly->vertices[i].lat_e7;
        int32_t xi = poly->vertices[i].lon_e7;
        int32_t yj = poly->vertices[j].lat_e7;
        int32_t xj = poly->vertices[j].lon_e7;

        if ((yi <= lat && lat < yj) || (yj <= lat && lat < yi)) {
            int64_t cross = (int64_t)(lon - xi) * (int64_t)(yj - yi) -
                            (int64_t)(lat - yi) * (int64_t)(xj - xi);

            if (yi < yj) {
                if (cross < 0) inside = !inside;
            } else {
                if (cross > 0) inside = !inside;
            }
        }
        j = i;
    }
    return inside;
}

// Перевірка циліндричної зони
static bool is_point_in_cylinder(const GeoPoint *p, const CylinderFence *cyl) {
    if (p->alt_m < cyl->alt_min || p->alt_m > cyl->alt_max) return false;

    // Відстань у площині через еквідистантну проєкцію
    float lat_rad = (float)cyl->center.lat_e7 * 1e-7f * (3.14159265f / 180.0f);
    float d_lat_m = (float)(p->lat_e7 - cyl->center.lat_e7) * 1e-7f * 111319.5f;
    float d_lon_m = (float)(p->lon_e7 - cyl->center.lon_e7) * 1e-7f * 111319.5f * cosf(lat_rad);

    return (d_lat_m * d_lat_m + d_lon_m * d_lon_m) <= (cyl->radius_m * cyl->radius_m);
}

// Повна перевірка належності дозволеному простору
bool geofence_check_point(const GeofenceEngine *engine, const GeoPoint *p) {
    bool has_keep_in = false;
    bool inside_keep_in = false;

    // 1. Перевірка полігонів
    for (uint8_t i = 0; i < engine->poly_count; i++) {
        if (!engine->polygons[i].active) continue;

        bool alt_ok = (p->alt_m >= engine->polygons[i].alt_min &&
                       p->alt_m <= engine->polygons[i].alt_max);

        bool in_poly_2d = is_point_in_polygon_fast(p->lat_e7, p->lon_e7, &engine->polygons[i]);
        bool inside_3d = alt_ok && in_poly_2d;

        if (engine->polygons[i].is_keep_in) {
            has_keep_in = true;
            if (inside_3d) inside_keep_in = true;
        } else {
            // Зона Keep-Out: вхід заборонено!
            if (inside_3d) return false;
        }
    }

    // 2. Перевірка циліндрів
    for (uint8_t i = 0; i < engine->cyl_count; i++) {
        if (!engine->cylinders[i].active) continue;

        bool in_cyl = is_point_in_cylinder(p, &engine->cylinders[i]);
        if (engine->cylinders[i].is_keep_in) {
            has_keep_in = true;
            if (in_cyl) inside_keep_in = true;
        } else {
            if (in_cyl) return false;
        }
    }

    if (has_keep_in && !inside_keep_in) return false;
    return true;
}

// Кінематична перевірка з гальмівним упередженням
bool geofence_predictive_check(const GeofenceEngine *engine,
                               const GeoPoint *p,
                               float vx_mps, float vy_mps, float vz_mps) {
    // 1. Перевірка поточної позиції
    if (!geofence_check_point(engine, p)) return false;

    float speed = sqrtf(vx_mps * vx_mps + vy_mps * vy_mps + vz_mps * vz_mps);
    if (speed < 0.1f) return true; // Дрон практично стоїть на місці

    // 2. Обчислення гальмівного шляху D_stop
    float d_stop = speed * engine->latency_sec +
                   (speed * speed) / (2.0f * engine->max_braking_accel) +
                   engine->static_margin_m;

    // 3. Розрахунок точки упередження P_pred
    float lookahead_ratio = d_stop / speed;
    float d_north_m = vx_mps * lookahead_ratio;
    float d_east_m  = vy_mps * lookahead_ratio;
    float d_alt_m   = vz_mps * lookahead_ratio;

    GeoPoint p_pred;
    p_pred.lat_e7 = p->lat_e7 + (int32_t)(d_north_m * (1e7f / 111319.5f));
    float lat_rad = (float)p->lat_e7 * 1e-7f * (3.14159265f / 180.0f);
    p_pred.lon_e7 = p->lon_e7 + (int32_t)(d_east_m * (1e7f / (111319.5f * cosf(lat_rad))));
    p_pred.alt_m  = p->alt_m + d_alt_m;

    // 4. Перевірка валідності точки упередження
    return geofence_check_point(engine, &p_pred);
}
