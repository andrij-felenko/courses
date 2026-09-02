/* Сценарій зі статті: 18 км над горбистим плато, вихід із попутним вітром
   і повернення проти нього. Той самий план проганяємо за трьох умов. */

#include <math.h>
#include <stdio.h>

#include "validate.h"

#define HOME_LAT 49.0000
#define HOME_LON 24.0000

/* Синтетичне підвікно рельєфу: плато 300 м і гряда 560 м поперек маршруту. */
static void build_dem(DemGrid *dem)
{
    const double lat0 = 48.9800;
    const double lon0 = 23.9700;
    const double cell = 0.0020;   /* ~222 м */

    if (!dem_init(dem, lat0, lon0, cell, DEM_MAX_SIDE, DEM_MAX_SIDE, 28.5f)) {
        return;
    }

    for (int r = 0; r < DEM_MAX_SIDE; r++) {
        const double lat = lat0 + cell * r;
        const double d   = (lat - 49.0450) / 0.0120;   /* гряда з центром на 49.045 */
        const float ridge = (float)(260.0 * exp(-d * d));

        for (int c = 0; c < DEM_MAX_SIDE; c++) {
            dem_set(dem, r, c, 300.0f + ridge);
        }
    }
}

static void build_plan(MissionPlan *plan, float cruise_msl_m)
{
    plan->count = 4;

    plan->items[0].pos = (GeoPoint){HOME_LAT, HOME_LON, 360.0f};
    plan->items[0].airspeed_mps = 15.0f;
    plan->items[0].loiter_s     = 0.0f;
    plan->items[0].survey       = false;

    plan->items[1].pos = (GeoPoint){49.0400, HOME_LON, cruise_msl_m};
    plan->items[1].airspeed_mps = 15.0f;
    plan->items[1].loiter_s     = 0.0f;
    plan->items[1].survey       = true;

    plan->items[2].pos = (GeoPoint){49.0800, HOME_LON, cruise_msl_m};
    plan->items[2].airspeed_mps = 15.0f;
    plan->items[2].loiter_s     = 60.0f;
    plan->items[2].survey       = true;

    plan->items[3].pos = (GeoPoint){HOME_LAT, HOME_LON, 380.0f};
    plan->items[3].airspeed_mps = 15.0f;
    plan->items[3].loiter_s     = 0.0f;
    plan->items[3].survey       = false;

    plan->safe_clearance_m      = 40.0f;
    plan->sample_step_m         = 15.0f;
    plan->min_ground_speed_mps  = 4.0f;
    plan->max_duration_s        = 3000.0f;
    plan->takeoff_wh            = 2.5f;
    plan->landing_wh            = 1.5f;

    plan->site_lat_deg          = HOME_LAT;
    plan->day_of_year           = 180;
    plan->start_hour_local      = 9.0f;
    plan->sunset_hour_local     = 20.5f;
    plan->min_sun_elevation_deg = 25.0f;
}

static void print_report(const char *title, const FeasReport *rep)
{
    printf("=== %s\n", title);
    printf("    вердикт        : %s\n", feas_status_text(rep->status));
    if (rep->detail[0] != '\0') {
        printf("    подробиця      : %s", rep->detail);
        if (rep->failed_leg >= 0) {
            printf(" (відрізок %d)", rep->failed_leg);
        }
        printf("\n");
    }
    printf("    маршрут        : %.0f м\n", (double)rep->total_distance_m);
    if (rep->total_time_s > 0.0f) {
        printf("    час            : %.0f с (%.1f хв)\n",
               (double)rep->total_time_s, (double)rep->total_time_s / 60.0);
    }
    if (rep->min_ground_speed_mps < 1.0e8f) {
        printf("    мін. шляхова   : %.1f м/с\n", (double)rep->min_ground_speed_mps);
    }
    if (rep->min_clearance_m < 1.0e8f) {
        printf("    мін. кліренс   : %.0f м\n", (double)rep->min_clearance_m);
    }
    if (rep->total_energy_wh > 0.0f) {
        printf("    енергія        : %.1f Вт·год з %.1f доступних (пік %.0f Вт / %.1f А)\n",
               (double)rep->total_energy_wh, (double)rep->usable_energy_wh,
               (double)rep->peak_power_w, (double)rep->peak_current_a);
    }
    if (rep->status == FEAS_OK) {
        printf("    резерв         : %.1f%%\n", (double)rep->reserve_left_pct);
        printf("    сонце (мін.)   : %.1f°\n", (double)rep->min_sun_elevation_deg);
        printf("    PSR            : точка %d, %.0f м від дому\n",
               rep->psr_item, (double)rep->psr_distance_m);
    }
    printf("\n");
}

int main(void)
{
    DemGrid dem;
    build_dem(&dem);

    /* Літак: маса 4.5 кг, крило 0.45 м², розмах 1.7 м. */
    Airframe ac = {
        .kind              = AIRFRAME_FIXED_WING,
        .mass_kg           = 4.5f,
        .eta_prop          = 0.58f,
        .avionics_w        = 18.0f,
        .airspeed_min_mps  = 12.0f,
        .airspeed_max_mps  = 24.0f,
        .max_climb_mps     = 3.5f,
        .wing_area_m2      = 0.45f,
        .cd0               = 0.045f,
        .span_m            = 1.70f,
        .oswald_e          = 0.80f,
        .disk_area_m2      = 0.0f,
        .body_drag_k       = 0.0f
    };

    /* 6S Li-Ion, 5.2 А·год, холодний ранок. */
    Battery bat = {
        .nominal_v       = 22.2f,
        .capacity_ah     = 5.2f,
        .peukert_k       = 1.08f,
        .ref_current_a   = 2.0f,
        .internal_r_ohm  = 0.05f,
        .pack_temp_c     = 8.0f,
        .health          = 0.92f,
        .reserve_margin  = 0.25f
    };

    const float rho = air_density(700.0f);
    float v_mp = 0.0f, v_mr = 0.0f;
    if (speed_min_power(&ac, rho, &v_mp) && speed_max_range(&ac, rho, &v_mr)) {
        printf("Опорні швидкості на 700 м: тривалість %.1f м/с, дальність %.1f м/с\n\n",
               (double)v_mp, (double)v_mr);
    }

    MissionPlan plan;
    FeasReport rep;

    /* 1. Помірний вітер із півдня: вихід попутний, повернення зустрічне. */
    build_plan(&plan, 700.0f);
    WindProfile calm = {.speed_mps = 3.0f, .from_deg = 180.0f,
                        .ref_height_m = 10.0f, .roughness_alpha = 0.22f};
    mission_validate(&plan, &calm, &dem, &ac, &bat, &rep);
    print_report("Вітер 3 м/с біля землі", &rep);

    /* 2. Той самий план, вітер удвічі сильніший — на висоті це вже 12 м/с. */
    build_plan(&plan, 700.0f);
    WindProfile strong = {.speed_mps = 6.0f, .from_deg = 180.0f,
                          .ref_height_m = 10.0f, .roughness_alpha = 0.22f};
    printf("Вітер на висоті 400 м: %.1f м/с (біля землі %.1f)\n",
           (double)wind_at_height(&strong, 400.0f), (double)strong.speed_mps);
    mission_validate(&plan, &strong, &dem, &ac, &bat, &rep);
    print_report("Вітер 6 м/с біля землі", &rep);

    /* 3. Помірний вітер, але низький ешелон: гряда 560 м посеред маршруту. */
    build_plan(&plan, 480.0f);
    mission_validate(&plan, &calm, &dem, &ac, &bat, &rep);
    print_report("Ешелон 480 м над гряддям 560 м", &rep);

    return 0;
}
