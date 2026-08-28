#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define MAX_MISSION_ITEMS 64
#define DEM_GRID_SIZE     32
#define M_PI_F            3.14159265358979323846f
#define DEG_TO_RAD        (M_PI_F / 180.0f)
#define METERS_PER_DEG    111320.0f

typedef enum {
    FEASIBILITY_OK = 0,
    ERR_EMPTY_MISSION,
    ERR_WIND_UNFEASIBLE,
    ERR_TERRAIN_COLLISION,
    ERR_CLIMB_RATE_EXCEEDED,
    ERR_INSUFFICIENT_ENERGY,
    ERR_TIME_WINDOW_EXCEEDED
} FeasibilityStatus;

typedef struct {
    double lat;          // Градуси широти
    double lon;          // Градуси довготи
    float  alt_msl;      // Абсолютна висота MSL, м
    float  airspeed;     // Бажана повітряна швидкість, м/с
    float  loiter_time;  // Час очікування/висіння, с
} Waypoint;

typedef struct {
    float speed;         // Швидкість вітру, м/с
    float direction_deg; // Звідки дме вітер (0 - північ, 90 - схід), градуси
} WindVector;

typedef struct {
    double origin_lat;
    double origin_lon;
    double cell_size_deg;
    float  elevations[DEM_GRID_SIZE][DEM_GRID_SIZE];
} DemMap;

typedef struct {
    float mass_kg;
    float max_climb_rate_mps;
    float p_hover_w;
    float p_avionics_w;
    float battery_capacity_wh;
    float reserve_margin; // Наприклад, 0.25 (25%)
} DroneModel;

typedef struct {
    FeasibilityStatus status;
    int   failed_leg_index;
    float total_distance_m;
    float total_time_s;
    float total_energy_wh;
    float min_terrain_clearance_m;
    float remaining_reserve_pct;
} FeasibilityReport;

// Білінійна інтерполяція висоти рельєфу за DEM-сіткою
static float sample_dem_altitude(const DemMap *dem, double lat, double lon) {
    double gx = (lon - dem->origin_lon) / dem->cell_size_deg;
    double gy = (lat - dem->origin_lat) / dem->cell_size_deg;

    if (gx < 0.0f || gx >= DEM_GRID_SIZE - 1 || gy < 0.0f || gy >= DEM_GRID_SIZE - 1) {
        return 0.0f; // За межами карти
    }

    int ix = (int)gx;
    int iy = (int)gy;
    float fx = (float)(gx - ix);
    float fy = (float)(gy - iy);

    float h00 = dem->elevations[iy][ix];
    float h10 = dem->elevations[iy][ix + 1];
    float h01 = dem->elevations[iy + 1][ix];
    float h11 = dem->elevations[iy + 1][ix + 1];

    float top = h00 * (1.0f - fx) + h10 * fx;
    float bot = h01 * (1.0f - fx) + h11 * fx;
    return top * (1.0f - fy) + bot * fy;
}

// Розрахунок відстані та азимута між двома координатами
static void calc_distance_bearing(double lat1, double lon1, double lat2, double lon2,
                                  float *dist_m, float *bearing_deg) {
    float d_lat = (float)((lat2 - lat1) * METERS_PER_DEG);
    float d_lon = (float)((lon2 - lon1) * METERS_PER_DEG * cos(lat1 * DEG_TO_RAD));
    *dist_m = sqrtf(d_lat * d_lat + d_lon * d_lon);

    float b_rad = atan2f(d_lon, d_lat);
    float b_deg = b_rad * (180.0f / M_PI_F);
    if (b_deg < 0.0f) b_deg += 360.0f;
    *bearing_deg = b_deg;
}

// Головна функція перевірки здійсненності місії
FeasibilityReport validate_mission(const Waypoint *wps, int count,
                                   const WindVector *wind,
                                   const DemMap *dem,
                                   const DroneModel *drone,
                                   float min_clearance_m,
                                   float max_allowed_time_s) {
    FeasibilityReport rep = {0};
    rep.status = FEASIBILITY_OK;
    rep.min_terrain_clearance_m = 9999.0f;

    if (count < 2) {
        rep.status = ERR_EMPTY_MISSION;
        return rep;
    }

    float total_e_joules = 0.0f;
    float total_time = 0.0f;
    float total_dist = 0.0f;

    for (int i = 0; i < count - 1; i++) {
        const Waypoint *w1 = &wps[i];
        const Waypoint *w2 = &wps[i + 1];

        float leg_dist = 0.0f, leg_bearing = 0.0f;
        calc_distance_bearing(w1->lat, w1->lon, w2->lat, w2->lon, &leg_dist, &leg_bearing);
        total_dist += leg_dist;

        // 1. Вітровий трикутник та шляхова швидкість
        float v_air = w2->airspeed;
        float wind_ang_rel = (wind->direction_deg - leg_bearing) * DEG_TO_RAD;
        float w_parallel = -wind->speed * cosf(wind_ang_rel); // Зустрічний = від'ємний
        float w_perp     =  wind->speed * sinf(wind_ang_rel);

        if (fabsf(w_perp) >= v_air) {
            rep.status = ERR_WIND_UNFEASIBLE;
            rep.failed_leg_index = i;
            return rep;
        }

        float sin_beta = w_perp / v_air;
        float cos_beta = sqrtf(1.0f - sin_beta * sin_beta);
        float v_ground = v_air * cos_beta + w_parallel;

        if (v_ground < 3.0f) { // Безпечний поріг мінімального поступу
            rep.status = ERR_WIND_UNFEASIBLE;
            rep.failed_leg_index = i;
            return rep;
        }

        float leg_time = leg_dist / v_ground;
        total_time += leg_time;

        // 2. Перевірка швидкопідйомності
        float delta_h = w2->alt_msl - w1->alt_msl;
        float req_climb_rate = delta_h / leg_time;
        if (req_climb_rate > drone->max_climb_rate_mps) {
            rep.status = ERR_CLIMB_RATE_EXCEEDED;
            rep.failed_leg_index = i;
            return rep;
        }

        // 3. Дискретна перевірка рельєфу на відрізку
        const float sample_step_m = 20.0f;
        int steps = (int)(leg_dist / sample_step_m);
        if (steps < 1) steps = 1;

        for (int s = 0; s <= steps; s++) {
            float alpha = (float)s / (float)steps;
            double cur_lat = w1->lat + (w2->lat - w1->lat) * alpha;
            double cur_lon = w1->lon + (w2->lon - w1->lon) * alpha;
            float cur_flight_alt = w1->alt_msl + delta_h * alpha;

            float terrain_alt = sample_dem_altitude(dem, cur_lat, cur_lon);
            float clearance = cur_flight_alt - terrain_alt;

            if (clearance < rep.min_terrain_clearance_m) {
                rep.min_terrain_clearance_m = clearance;
            }

            if (clearance < min_clearance_m) {
                rep.status = ERR_TERRAIN_COLLISION;
                rep.failed_leg_index = i;
                return rep;
            }
        }

        // 4. Енергетичний розрахунок відрізка
        float p_aero = drone->p_hover_w * (1.0f + 0.05f * powf(v_air / 10.0f, 3.0f));
        float p_climb = (delta_h > 0.0f) ? (drone->mass_kg * 9.81f * req_climb_rate / 0.65f) : 0.0f;
        float p_leg_total = p_aero + p_climb + drone->p_avionics_w;

        total_e_joules += p_leg_total * leg_time;

        // Врахування зависання на точці
        if (w2->loiter_time > 0.0f) {
            total_time += w2->loiter_time;
            total_e_joules += (drone->p_hover_w + drone->p_avionics_w) * w2->loiter_time;
        }
    }

    rep.total_distance_m = total_dist;
    rep.total_time_s     = total_time;
    rep.total_energy_wh  = total_e_joules / 3600.0f;

    // 5. Перевірка обмеження часу
    if (total_time > max_allowed_time_s) {
        rep.status = ERR_TIME_WINDOW_EXCEEDED;
        return rep;
    }

    // 6. Перевірка енергетичного бюджету та резерву
    float usable_battery_wh = drone->battery_capacity_wh * (1.0f - drone->reserve_margin);
    if (rep.total_energy_wh > usable_battery_wh) {
        rep.status = ERR_INSUFFICIENT_ENERGY;
        return rep;
    }

    float used_pct = rep.total_energy_wh / drone->battery_capacity_wh;
    rep.remaining_reserve_pct = (1.0f - used_pct) * 100.0f;

    return rep;
}
