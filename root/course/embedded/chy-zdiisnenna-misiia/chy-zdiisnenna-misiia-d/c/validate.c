#include "validate.h"

#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    float dist_m;
    float time_s;
    float ground_speed_mps;
    float energy_wh_at_end;   /* накопичена витрата на момент прибуття у вейпойнт i+1 */
} LegState;

const char *feas_status_text(FeasStatus status)
{
    switch (status) {
    case FEAS_OK:                return "GO — місія здійсненна";
    case FEAS_ERR_PLAN:          return "план некоректний";
    case FEAS_ERR_WIND:          return "боковий вітер сильніший за повітряну швидкість";
    case FEAS_ERR_GROUND_SPEED:  return "шляхова швидкість нижча за поріг";
    case FEAS_ERR_DEM_GAP:       return "маршрут виходить за межі карти висот";
    case FEAS_ERR_TERRAIN:       return "недостатній кліренс над рельєфом";
    case FEAS_ERR_CLIMB:         return "потрібна швидкопідйомність вища за можливу";
    case FEAS_ERR_POWER:         return "потрібна потужність недосяжна для батареї";
    case FEAS_ERR_ENERGY:        return "енергії не вистачає з урахуванням резерву";
    case FEAS_ERR_NO_RETURN:     return "точку безпечного повернення пройдено";
    case FEAS_ERR_TIME_WINDOW:   return "місія не вкладається в операційне вікно";
    case FEAS_ERR_SUNSET:        return "посадка пізніше за дозволений час до заходу сонця";
    case FEAS_ERR_SUN_LOW:       return "сонце надто низько для оптичного навантаження";
    default:                     return "невідомий стан";
    }
}

static float solar_declination_deg(int day_of_year)
{
    const float arg_deg = (360.0f / 365.0f) * (float)(day_of_year - 81);
    return 23.45f * sinf((float)(arg_deg * GEO_DEG_TO_RAD));
}

float solar_elevation_deg(double lat_deg, int day_of_year, float solar_hour)
{
    const double phi   = lat_deg * GEO_DEG_TO_RAD;
    const double delta = (double)solar_declination_deg(day_of_year) * GEO_DEG_TO_RAD;
    const double hour  = (15.0 * ((double)solar_hour - 12.0)) * GEO_DEG_TO_RAD;

    double sin_alpha = sin(phi) * sin(delta) + cos(phi) * cos(delta) * cos(hour);
    if (sin_alpha > 1.0) {
        sin_alpha = 1.0;
    }
    if (sin_alpha < -1.0) {
        sin_alpha = -1.0;
    }
    return (float)(asin(sin_alpha) * GEO_RAD_TO_DEG);
}

static FeasStatus fail(FeasReport *rep, FeasStatus status, int leg, const char *fmt, ...)
{
    va_list ap;
    rep->status     = status;
    rep->failed_leg = leg;

    va_start(ap, fmt);
    vsnprintf(rep->detail, sizeof rep->detail, fmt, ap);
    va_end(ap);

    return status;
}

/* Перший бар'єр: формат плану й ліміти швидкостей. */
static FeasStatus check_plan(const MissionPlan *plan, const Airframe *ac, FeasReport *rep)
{
    if (plan->count < 2 || plan->count > MISSION_MAX_ITEMS) {
        return fail(rep, FEAS_ERR_PLAN, -1, "точок у плані: %d", plan->count);
    }

    for (int i = 0; i < plan->count; i++) {
        const MissionItem *it = &plan->items[i];

        if (!isfinite(it->pos.lat_deg) || !isfinite(it->pos.lon_deg) ||
            !isfinite(it->pos.alt_msl_m)) {
            return fail(rep, FEAS_ERR_PLAN, i, "точка %d: нечислові координати", i);
        }
        if (it->pos.lat_deg < -90.0 || it->pos.lat_deg > 90.0 ||
            it->pos.lon_deg < -180.0 || it->pos.lon_deg > 180.0) {
            return fail(rep, FEAS_ERR_PLAN, i, "точка %d: координати поза межами", i);
        }
        if (it->loiter_s < 0.0f) {
            return fail(rep, FEAS_ERR_PLAN, i, "точка %d: від'ємний час очікування", i);
        }
        if (i > 0 && (it->airspeed_mps < ac->airspeed_min_mps ||
                      it->airspeed_mps > ac->airspeed_max_mps)) {
            return fail(rep, FEAS_ERR_PLAN, i,
                        "точка %d: швидкість %.1f поза діапазоном %.1f...%.1f м/с",
                        i, (double)it->airspeed_mps,
                        (double)ac->airspeed_min_mps, (double)ac->airspeed_max_mps);
        }
    }
    return FEAS_OK;
}

/* Висота над землею в точці — потрібна і вітру (закон Гельмана), і кліренсу. */
static bool height_agl(const DemGrid *dem, GeoPoint p, float *out_agl_m)
{
    float terrain_msl = 0.0f;
    if (!dem_sample_msl(dem, p.lat_deg, p.lon_deg, &terrain_msl)) {
        return false;
    }
    *out_agl_m = p.alt_msl_m - terrain_msl;
    return true;
}

FeasStatus mission_validate(const MissionPlan *plan,
                            const WindProfile *wind,
                            const DemGrid *dem,
                            const Airframe *ac,
                            const Battery *bat,
                            FeasReport *rep)
{
    LegState legs[MISSION_MAX_ITEMS];
    float energy_wh = 0.0f;
    float elapsed_s = 0.0f;

    memset(rep, 0, sizeof *rep);
    rep->status                = FEAS_OK;
    rep->failed_leg            = -1;
    rep->min_clearance_m       = 1.0e9f;
    rep->min_ground_speed_mps  = 1.0e9f;
    rep->min_sun_elevation_deg = 90.0f;
    rep->psr_item              = 0;

    if (check_plan(plan, ac, rep) != FEAS_OK) {
        return rep->status;
    }

    energy_wh = plan->takeoff_wh;

    for (int i = 0; i < plan->count - 1; i++) {
        const MissionItem *from = &plan->items[i];
        const MissionItem *to   = &plan->items[i + 1];

        const float leg_dist  = geo_distance_m(from->pos, to->pos);
        const float track_deg = geo_bearing_deg(from->pos, to->pos);
        const float v_air     = to->airspeed_mps;

        if (leg_dist < 1.0f) {
            return fail(rep, FEAS_ERR_PLAN, i, "відрізок %d вироджений (%.1f м)",
                        i, (double)leg_dist);
        }
        rep->total_distance_m += leg_dist;

        /* 1. Вітрове вікно. Вітер беремо на середній висоті відрізка. */
        const GeoPoint mid = geo_lerp(from->pos, to->pos, 0.5f);
        float mid_agl = 0.0f;
        if (!height_agl(dem, mid, &mid_agl)) {
            return fail(rep, FEAS_ERR_DEM_GAP, i, "відрізок %d поза підвікном DEM", i);
        }

        LegWind lw;
        if (!wind_solve_leg(wind, track_deg, mid_agl, v_air, &lw)) {
            return fail(rep, FEAS_ERR_WIND, i,
                        "відрізок %d: вітер %.1f м/с проти повітряної %.1f м/с",
                        i, (double)wind_at_height(wind, mid_agl), (double)v_air);
        }
        if (lw.ground_speed_mps < rep->min_ground_speed_mps) {
            rep->min_ground_speed_mps = lw.ground_speed_mps;
        }
        if (lw.ground_speed_mps < plan->min_ground_speed_mps) {
            return fail(rep, FEAS_ERR_GROUND_SPEED, i,
                        "відрізок %d: шляхова %.1f м/с (вітер %.1f м/с, поріг %.1f)",
                        i, (double)lw.ground_speed_mps, (double)lw.speed_mps,
                        (double)plan->min_ground_speed_mps);
        }

        const float leg_time = leg_dist / lw.ground_speed_mps;

        /* 2. Градієнт набору висоти. */
        const float delta_h    = to->pos.alt_msl_m - from->pos.alt_msl_m;
        const float climb_rate = delta_h / leg_time;
        if (climb_rate > ac->max_climb_mps) {
            return fail(rep, FEAS_ERR_CLIMB, i,
                        "відрізок %d: треба %.2f м/с набору, апарат дає %.2f",
                        i, (double)climb_rate, (double)ac->max_climb_mps);
        }

        /* 3. Кліренс над рельєфом по всій довжині відрізка. */
        TerrainScan scan;
        if (!terrain_scan_leg(dem, from->pos, to->pos,
                              plan->sample_step_m, plan->safe_clearance_m, &scan)) {
            return fail(rep, FEAS_ERR_DEM_GAP, i, "відрізок %d поза підвікном DEM", i);
        }
        if (scan.min_clearance_m < rep->min_clearance_m) {
            rep->min_clearance_m = scan.min_clearance_m;
        }
        if (scan.collision) {
            return fail(rep, FEAS_ERR_TERRAIN, i,
                        "відрізок %d: кліренс %.0f м на %.0f м від початку (треба %.0f)",
                        i, (double)scan.min_clearance_m, (double)scan.min_clearance_dist_m,
                        (double)plan->safe_clearance_m);
        }

        /* 4. Енергія відрізка. */
        const float rho     = air_density(mid.alt_msl_m);
        const float p_leg   = power_level_w(ac, v_air, rho)
                            + power_climb_w(ac, climb_rate)
                            + ac->avionics_w;
        float current_a = 0.0f;
        if (!battery_current_a(bat, p_leg, &current_a)) {
            return fail(rep, FEAS_ERR_POWER, i, "відрізок %d: потрібно %.0f Вт", i, (double)p_leg);
        }
        if (p_leg > rep->peak_power_w) {
            rep->peak_power_w   = p_leg;
            rep->peak_current_a = current_a;
        }

        energy_wh += p_leg * leg_time / 3600.0f;
        elapsed_s += leg_time;

        /* 5. Сонце над ділянкою зйомки — на середині проходу відрізка. */
        if (to->survey) {
            const float solar_hour = plan->start_hour_local + (elapsed_s - leg_time * 0.5f) / 3600.0f;
            const float sun = solar_elevation_deg(plan->site_lat_deg, plan->day_of_year, solar_hour);
            if (sun < rep->min_sun_elevation_deg) {
                rep->min_sun_elevation_deg = sun;
            }
            if (sun < plan->min_sun_elevation_deg) {
                return fail(rep, FEAS_ERR_SUN_LOW, i,
                            "відрізок %d: сонце %.1f° (треба %.1f°)",
                            i, (double)sun, (double)plan->min_sun_elevation_deg);
            }
        }

        /* Очікування на точці: висіння для коптера, віраж для літака. */
        if (to->loiter_s > 0.0f) {
            const float p_loiter = power_loiter_w(ac, rho) + ac->avionics_w;
            energy_wh += p_loiter * to->loiter_s / 3600.0f;
            elapsed_s += to->loiter_s;
        }

        legs[i].dist_m           = leg_dist;
        legs[i].time_s           = leg_time;
        legs[i].ground_speed_mps = lw.ground_speed_mps;
        legs[i].energy_wh_at_end = energy_wh;
    }

    energy_wh += plan->landing_wh;
    rep->total_time_s     = elapsed_s;
    rep->total_energy_wh  = energy_wh;

    /* Доступна ємність залежить від середнього струму — тому рахуємо її
       після проходу всіх відрізків, за фактичною середньою потужністю. */
    float avg_current_a = 0.0f;
    if (elapsed_s > 0.0f) {
        const float avg_power_w = energy_wh * 3600.0f / elapsed_s;
        if (!battery_current_a(bat, avg_power_w, &avg_current_a)) {
            return fail(rep, FEAS_ERR_POWER, -1, "середня потужність %.0f Вт недосяжна",
                        (double)avg_power_w);
        }
    }
    rep->delivered_energy_wh = battery_delivered_wh(bat, avg_current_a);
    rep->usable_energy_wh    = battery_usable_wh(bat, avg_current_a);

    /* 6. Часове вікно й захід сонця. */
    if (elapsed_s > plan->max_duration_s) {
        return fail(rep, FEAS_ERR_TIME_WINDOW, -1, "%.0f с проти дозволених %.0f с",
                    (double)elapsed_s, (double)plan->max_duration_s);
    }
    {
        const float finish_hour = plan->start_hour_local + elapsed_s / 3600.0f;
        const float deadline    = plan->sunset_hour_local - 0.5f;   /* 30 хв до сутінків */
        if (finish_hour > deadline) {
            return fail(rep, FEAS_ERR_SUNSET, -1, "посадка о %.2f, крайній строк %.2f",
                        (double)finish_hour, (double)deadline);
        }
    }

    /* 7. Енергетичний баланс. */
    if (energy_wh > rep->usable_energy_wh) {
        return fail(rep, FEAS_ERR_ENERGY, -1, "потрібно %.1f Вт·год, доступно %.1f Вт·год",
                    (double)energy_wh, (double)rep->usable_energy_wh);
    }
    rep->reserve_left_pct = (rep->delivered_energy_wh - energy_wh) /
                            rep->delivered_energy_wh * 100.0f;

    /* 8. Точка безпечного повернення: у кожному вейпойнті звіряємо залишок
       із енергією прямого повернення додому проти поточного вітру. */
    {
        const GeoPoint home = plan->items[0].pos;
        const float reserve_wh = bat->reserve_margin * battery_nominal_wh(bat);

        for (int k = 1; k < plan->count; k++) {
            const MissionItem *it = &plan->items[k];
            const float dist_home = geo_distance_m(it->pos, home);
            if (dist_home < 1.0f) {
                rep->psr_item = k;
                continue;
            }

            float agl = 0.0f;
            if (!height_agl(dem, it->pos, &agl)) {
                return fail(rep, FEAS_ERR_DEM_GAP, k, "точка %d поза підвікном DEM", k);
            }

            const float v_air = it->airspeed_mps;
            LegWind back;
            if (!wind_solve_leg(wind, geo_bearing_deg(it->pos, home), agl, v_air, &back) ||
                back.ground_speed_mps < plan->min_ground_speed_mps) {
                return fail(rep, FEAS_ERR_NO_RETURN, k,
                            "з точки %d повернення проти вітру неможливе", k);
            }

            const float rho    = air_density(it->pos.alt_msl_m);
            const float p_back = power_level_w(ac, v_air, rho) + ac->avionics_w;
            const float e_rtl  = p_back * (dist_home / back.ground_speed_mps) / 3600.0f
                               + plan->landing_wh;
            const float remaining = rep->delivered_energy_wh - legs[k - 1].energy_wh_at_end;

            if (remaining - e_rtl < reserve_wh) {
                return fail(rep, FEAS_ERR_NO_RETURN, k,
                            "у точці %d залишок %.1f, повернення коштує %.1f, резерв %.1f Вт·год",
                            k, (double)remaining, (double)e_rtl, (double)reserve_wh);
            }
            rep->psr_item     = k;
            rep->psr_distance_m = dist_home;
        }
    }

    rep->status = FEAS_OK;
    snprintf(rep->detail, sizeof rep->detail, "усі п'ять бар'єрів пройдено");
    return FEAS_OK;
}
