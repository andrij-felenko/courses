#ifndef VALIDATE_H
#define VALIDATE_H

#include <stdbool.h>

#include "energy.h"
#include "geo.h"
#include "terrain.h"
#include "wind.h"

#define MISSION_MAX_ITEMS 64

typedef struct {
    GeoPoint pos;
    float    airspeed_mps;
    float    loiter_s;
    bool     survey;      /* ділянка зйомки: потрібне достатньо високе сонце */
} MissionItem;

typedef struct {
    MissionItem items[MISSION_MAX_ITEMS];
    int   count;

    float safe_clearance_m;      /* h_safe: 30...50 м */
    float sample_step_m;         /* крок проби рельєфу */
    float min_ground_speed_mps;  /* поріг здійсненності за вітром, 3...5 м/с */
    float max_duration_s;        /* операційне вікно */
    float takeoff_wh;
    float landing_wh;

    double site_lat_deg;
    int    day_of_year;
    float  start_hour_local;     /* місцевий сонячний час старту */
    float  sunset_hour_local;
    float  min_sun_elevation_deg;
} MissionPlan;

typedef enum {
    FEAS_OK = 0,
    FEAS_ERR_PLAN,
    FEAS_ERR_WIND,
    FEAS_ERR_GROUND_SPEED,
    FEAS_ERR_DEM_GAP,
    FEAS_ERR_TERRAIN,
    FEAS_ERR_CLIMB,
    FEAS_ERR_POWER,
    FEAS_ERR_ENERGY,
    FEAS_ERR_NO_RETURN,
    FEAS_ERR_TIME_WINDOW,
    FEAS_ERR_SUNSET,
    FEAS_ERR_SUN_LOW
} FeasStatus;

typedef struct {
    FeasStatus status;
    int   failed_leg;              /* -1, якщо відмова не прив'язана до відрізка */
    char  detail[128];

    float total_distance_m;
    float total_time_s;
    float total_energy_wh;
    float delivered_energy_wh;     /* що батарея віддасть без чіпання резерву */
    float usable_energy_wh;        /* бюджет місії */
    float reserve_left_pct;

    float min_clearance_m;
    float min_ground_speed_mps;
    float peak_power_w;
    float peak_current_a;
    float min_sun_elevation_deg;

    int   psr_item;                /* останній вейпойнт, з якого ще вистачає на повернення */
    float psr_distance_m;          /* відстань від дому до цього вейпойнта */
} FeasReport;

const char *feas_status_text(FeasStatus status);

float solar_elevation_deg(double lat_deg, int day_of_year, float solar_hour);

FeasStatus mission_validate(const MissionPlan *plan,
                            const WindProfile *wind,
                            const DemGrid *dem,
                            const Airframe *ac,
                            const Battery *bat,
                            FeasReport *rep);

#endif /* VALIDATE_H */
