#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define SPEED_OF_LIGHT 299792458.0
#define EARTH_RADIUS_EFF 8495000.0  /* 4/3 * 6371000 м */

typedef struct {
    double dist_from_tx_m;
    double ground_alt_m;
    double clutter_height_m;
} TerrainPoint;

typedef struct {
    double r1_radius_m;
    double earth_bulge_m;
    double los_height_m;
    double obstacle_top_m;
    double clearance_m;
    double clearance_ratio;
    double diffraction_loss_db;
    bool is_60_percent_clear;
} ClearanceResult;

/* Апроксимація дифракційних втрат за ITU-R P.526 */
static double calculate_itu_loss(double v) {
    if (v <= -0.78) {
        return 0.0;
    }
    double term = sqrt((v - 0.1) * (v - 0.1) + 1.0) + (v - 0.1);
    return 6.9 + 20.0 * log10(term);
}

ClearanceResult evaluate_clearance(
    double freq_hz,
    double total_distance_m,
    double tx_total_alt_m,
    double rx_total_alt_m,
    TerrainPoint obstacle
) {
    ClearanceResult res;
    double lambda = SPEED_OF_LIGHT / freq_hz;
    double d1 = obstacle.dist_from_tx_m;
    double d2 = total_distance_m - d1;

    /* 1. Радіус першої зони Френеля */
    res.r1_radius_m = sqrt((lambda * d1 * d2) / total_distance_m);

    /* 2. Кривина Землі зі стандартною рефракцією (k = 4/3) */
    res.earth_bulge_m = (d1 * d2) / (2.0 * EARTH_RADIUS_EFF);

    /* 3. Висота лінії прямої видимості (LOS) у точці перешкоди */
    double slope = (rx_total_alt_m - tx_total_alt_m) / total_distance_m;
    res.los_height_m = tx_total_alt_m + slope * d1;

    /* 4. Повна висота перешкоди з урахуванням рельєфу, дерев та горба Землі */
    res.obstacle_top_m = obstacle.ground_alt_m + obstacle.clutter_height_m + res.earth_bulge_m;

    /* 5. Кліренс: додатний, якщо є вільний просвіт (перешкода нижче LOS) */
    res.clearance_m = res.los_height_m - res.obstacle_top_m;
    res.clearance_ratio = res.clearance_m / res.r1_radius_m;

    /* 6. Дифракційний параметр v = -h_clearance * sqrt(2) / r1 */
    double h_obstacle_rel = -res.clearance_m;
    double v = sqrt(2.0) * (h_obstacle_rel / res.r1_radius_m);

    res.diffraction_loss_db = calculate_itu_loss(v);
    res.is_60_percent_clear = (res.clearance_ratio >= 0.60);

    return res;
}
