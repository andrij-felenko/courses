#include "terrain.h"

#include <math.h>

bool dem_init(DemGrid *dem, double lat0, double lon0, double cell_deg,
              int rows, int cols, float geoid_undulation_m)
{
    if (rows < 2 || cols < 2 || rows > DEM_MAX_SIDE || cols > DEM_MAX_SIDE) {
        return false;
    }
    if (!(cell_deg > 0.0)) {
        return false;
    }

    dem->origin_lat_deg     = lat0;
    dem->origin_lon_deg     = lon0;
    dem->cell_deg           = cell_deg;
    dem->rows               = rows;
    dem->cols               = cols;
    dem->geoid_undulation_m = geoid_undulation_m;

    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
            dem->node_m[r][c] = 0.0f;
        }
    }
    return true;
}

bool dem_set(DemGrid *dem, int row, int col, float elevation_msl_m)
{
    if (row < 0 || col < 0 || row >= dem->rows || col >= dem->cols) {
        return false;
    }
    dem->node_m[row][col] = elevation_msl_m;
    return true;
}

float dem_msl_from_ellipsoidal(const DemGrid *dem, float height_wgs84_m)
{
    return height_wgs84_m - dem->geoid_undulation_m;
}

bool dem_sample_msl(const DemGrid *dem, double lat_deg, double lon_deg, float *out_msl_m)
{
    const double gx = (lon_deg - dem->origin_lon_deg) / dem->cell_deg;
    const double gy = (lat_deg - dem->origin_lat_deg) / dem->cell_deg;

    if (!(gx >= 0.0) || !(gy >= 0.0) ||
        gx > (double)(dem->cols - 1) || gy > (double)(dem->rows - 1)) {
        return false;   /* поза підвікном рельєфу */
    }

    int ix = (int)floor(gx);
    int iy = (int)floor(gy);
    /* Точка рівно на верхній межі: беремо останню повну комірку. */
    if (ix > dem->cols - 2) {
        ix = dem->cols - 2;
    }
    if (iy > dem->rows - 2) {
        iy = dem->rows - 2;
    }

    const float fx = (float)(gx - (double)ix);
    const float fy = (float)(gy - (double)iy);

    const float h00 = dem->node_m[iy][ix];
    const float h10 = dem->node_m[iy][ix + 1];
    const float h01 = dem->node_m[iy + 1][ix];
    const float h11 = dem->node_m[iy + 1][ix + 1];

    const float top = h00 * (1.0f - fx) + h10 * fx;
    const float bot = h01 * (1.0f - fx) + h11 * fx;

    *out_msl_m = top * (1.0f - fy) + bot * fy;
    return true;
}

bool terrain_scan_leg(const DemGrid *dem, GeoPoint a, GeoPoint b,
                      float step_m, float safe_clearance_m, TerrainScan *out)
{
    const float leg_dist = geo_distance_m(a, b);

    out->min_clearance_m      = 1.0e9f;
    out->min_clearance_dist_m = 0.0f;
    out->worst_point          = a;
    out->collision            = false;

    if (step_m < 1.0f) {
        step_m = 1.0f;
    }

    /* Крок дискретизації беруть не більшим за половину комірки DEM,
       інакше пагорб між двома пробами лишається непоміченим. */
    int steps = (int)ceilf(leg_dist / step_m);
    if (steps < 1) {
        steps = 1;
    }

    for (int s = 0; s <= steps; s++) {
        const float t = (float)s / (float)steps;
        const GeoPoint p = geo_lerp(a, b, t);

        float terrain_msl = 0.0f;
        if (!dem_sample_msl(dem, p.lat_deg, p.lon_deg, &terrain_msl)) {
            return false;
        }

        const float clearance = p.alt_msl_m - terrain_msl;
        if (clearance < out->min_clearance_m) {
            out->min_clearance_m      = clearance;
            out->min_clearance_dist_m = leg_dist * t;
            out->worst_point          = p;
        }
        if (clearance < safe_clearance_m) {
            out->collision = true;
            return true;   /* далі рахувати нема сенсу: точка колізії знайдена */
        }
    }
    return true;
}
