#ifndef TERRAIN_H
#define TERRAIN_H

#include <stdbool.h>

#include "geo.h"

/* Підвікно рельєфу, вирізане з .HGT за охопленням місії. Уся сітка живе
   в статичній пам'яті: динамічного виділення в бортовому коді немає. */
#define DEM_MAX_SIDE 64

typedef struct {
    double origin_lat_deg;      /* південно-західний вузол сітки */
    double origin_lon_deg;
    double cell_deg;            /* крок сітки в градусах */
    int    rows;
    int    cols;
    float  geoid_undulation_m;  /* N: h_wgs84 = H_msl + N */
    float  node_m[DEM_MAX_SIDE][DEM_MAX_SIDE];  /* ортометричні висоти */
} DemGrid;

typedef struct {
    float    min_clearance_m;
    float    min_clearance_dist_m;  /* відстань від початку відрізка до найгіршої точки */
    GeoPoint worst_point;
    bool     collision;             /* кліренс упав нижче безпечного буфера */
} TerrainScan;

bool dem_init(DemGrid *dem, double lat0, double lon0, double cell_deg,
              int rows, int cols, float geoid_undulation_m);

bool dem_set(DemGrid *dem, int row, int col, float elevation_msl_m);

/* Білінійна інтерполяція між чотирма вузлами.
   false — точка поза підвікном: даних немає, і це відмова, а не нуль. */
bool dem_sample_msl(const DemGrid *dem, double lat_deg, double lon_deg, float *out_msl_m);

/* Приведення висоти GNSS (над еліпсоїдом WGS-84) до MSL моделі рельєфу. */
float dem_msl_from_ellipsoidal(const DemGrid *dem, float height_wgs84_m);

/* Прохід відрізка з кроком step_m. false — на маршруті трапилася прогалина DEM. */
bool terrain_scan_leg(const DemGrid *dem, GeoPoint a, GeoPoint b,
                      float step_m, float safe_clearance_m, TerrainScan *out);

#endif /* TERRAIN_H */
