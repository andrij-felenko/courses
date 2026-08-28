#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define DEG_TO_RAD (3.14159265358979323846 / 180.0)
#define RAD_TO_DEG (180.0 / 3.14159265358979323846)
#define EARTH_RADIUS_M 6371000.0

/* Структура географічних координат */
typedef struct {
    double lat; /* широта в градусах */
    double lon; /* довгота в градусах */
    double alt; /* висота в метрах над рівнем моря */
} GeoCoord;

/* Розраховані кути стеження */
typedef struct {
    double azimuth_deg;   /* 0..360 градусів від True North */
    double elevation_deg; /* 0..90 градусів від горизонту */
    double distance_m;    /* пряма відстань до цілі */
} TrackerAngles;

/* Стан фільтрації та приводів трекера */
typedef struct {
    GeoCoord home;
    bool has_home;
    double current_azimuth;
    double current_elevation;
    double max_slew_rate_deg_s; /* максимальна швидкість град/с */
    double deadband_deg;        /* поріг нечутливості */
} TrackerController;

/* Ініціалізація контролера */
void tracker_init(TrackerController *tc, double max_slew_rate, double deadband) {
    tc->has_home = false;
    tc->current_azimuth = 0.0;
    tc->current_elevation = 0.0;
    tc->max_slew_rate_deg_s = max_slew_rate;
    tc->deadband_deg = deadband;
}

/* Встановлення домашньої позиції наземної станції */
void tracker_set_home(TrackerController *tc, double lat, double lon, double alt) {
    tc->home.lat = lat;
    tc->home.lon = lon;
    tc->home.alt = alt;
    tc->has_home = true;
}

/* Обчислення сферичного азимуту та елевації */
TrackerAngles tracker_calculate(const GeoCoord *home, const GeoCoord *target) {
    TrackerAngles res = {0.0, 0.0, 0.0};

    double phi1 = home->lat * DEG_TO_RAD;
    double phi2 = target->lat * DEG_TO_RAD;
    double delta_phi = (target->lat - home->lat) * DEG_TO_RAD;
    double delta_lambda = (target->lon - home->lon) * DEG_TO_RAD;

    /* Розрахунок ортодромічної горизонтальної відстані (Haversine) */
    double a = sin(delta_phi / 2.0) * sin(delta_phi / 2.0) +
               cos(phi1) * cos(phi2) *
               sin(delta_lambda / 2.0) * sin(delta_lambda / 2.0);
    double c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));
    double ground_distance = EARTH_RADIUS_M * c;

    /* Розрахунок азимуту (Bearing) */
    double y = sin(delta_lambda) * cos(phi2);
    double x = cos(phi1) * sin(phi2) - sin(phi1) * cos(phi2) * cos(delta_lambda);
    double az_rad = atan2(y, x);
    double az_deg = az_rad * RAD_TO_DEG;
    if (az_deg < 0.0) {
        az_deg += 360.0;
    }

    /* Різниця висот з корекцією на кривину Землі */
    double earth_curvature = (ground_distance * ground_distance) / (2.0 * EARTH_RADIUS_M);
    double delta_alt = (target->alt - home->alt) - earth_curvature;

    /* Розрахунок кута елевації */
    double el_rad = atan2(delta_alt, ground_distance);
    double el_deg = el_rad * RAD_TO_DEG;
    if (el_deg < 0.0) el_deg = 0.0;
    if (el_deg > 90.0) el_deg = 90.0;

    res.azimuth_deg = az_deg;
    res.elevation_deg = el_deg;
    res.distance_m = sqrt(ground_distance * ground_distance + delta_alt * delta_alt);

    return res;
}

/* Оновлення положення з фільтрацією deadband та slew rate */
void tracker_update(TrackerController *tc, const GeoCoord *target, double dt_sec, uint16_t *pwm_pan, uint16_t *pwm_tilt) {
    if (!tc->has_home) return;

    TrackerAngles target_angles = tracker_calculate(&tc->home, target);

    /* Найкоротша кутова різниця для азимуту (-180..+180) */
    double diff_az = target_angles.azimuth_deg - tc->current_azimuth;
    while (diff_az > 180.0) diff_az -= 360.0;
    while (diff_az < -180.0) diff_az += 360.0;

    /* Перевірка зони нечутливості */
    if (fabs(diff_az) > tc->deadband_deg) {
        double max_step = tc->max_slew_rate_deg_s * dt_sec;
        if (diff_az > max_step) diff_az = max_step;
        if (diff_az < -max_step) diff_az = -max_step;

        tc->current_azimuth += diff_az;
        if (tc->current_azimuth >= 360.0) tc->current_azimuth -= 360.0;
        if (tc->current_azimuth < 0.0) tc->current_azimuth += 360.0;
    }

    /* Елевація */
    double diff_el = target_angles.elevation_deg - tc->current_elevation;
    if (fabs(diff_el) > tc->deadband_deg) {
        double max_step = tc->max_slew_rate_deg_s * dt_sec;
        if (diff_el > max_step) diff_el = max_step;
        if (diff_el < -max_step) diff_el = -max_step;
        tc->current_elevation += diff_el;
    }

    /* Конвертація кутів у ШІМ (1000..2000 мкс): Pan 0..360, Tilt 0..90 */
    *pwm_pan = (uint16_t)(1000.0 + (tc->current_azimuth / 360.0) * 1000.0);
    *pwm_tilt = (uint16_t)(1000.0 + (tc->current_elevation / 90.0) * 1000.0);
}
