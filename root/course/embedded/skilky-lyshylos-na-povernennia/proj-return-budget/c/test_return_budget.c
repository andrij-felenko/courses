/*
 * Польотні сценарії з розділу «Верифікація». Збірка на хості:
 *   cc -std=c11 -O2 -o test_return_budget test_return_budget.c return_budget.c -lm
 */
#include "return_budget.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

static int g_failures;

static void check(bool ok, const char* what) {
    printf("  %s %s\n", ok ? "[ok]" : "[FAIL]", what);
    if (!ok) ++g_failures;
}

static bool approx(float a, float b, float eps) {
    return fabsf(a - b) <= eps;
}

/* Планер із розділу 3: калібрована поляра й 6S-пакет */
static return_config_t make_config(void) {
    return_config_t cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.v_air_min_ms           = 12.0f;
    cfg.v_air_max_ms           = 28.0f;
    cfg.v_best_range_still_ms  = 16.0f;
    cfg.c_ind                  = 1500.0f;
    cfg.c_par                  = 0.02f;
    cfg.p_avionics_watts       = 12.0f;
    cfg.rtl_safe_altitude_m    = 80.0f;
    cfg.v_climb_ms             = 3.0f;
    cfg.p_climb_watts          = 450.0f;
    cfg.p_hover_watts          = 900.0f;
    cfg.t_land_maneuver_sec    = 25.0f;
    cfg.reserve_margin_ratio   = 0.25f;
    cfg.filter_time_constant_s = 8.0f;
    cfg.nominal_energy_wh      = 220.0f;
    cfg.cell_v_cutoff          = 3.3f;
    cfg.cell_count             = 6;
    return cfg;
}

/* База за 2 км на північ, борт на 100 м, штиль, повний пакет */
static return_telemetry_t make_telemetry(float distance_north_m, float alt_m) {
    return_telemetry_t t;
    memset(&t, 0, sizeof(t));
    t.pos_current_ned[0] = 0.0f;
    t.pos_current_ned[1] = 0.0f;
    t.pos_current_ned[2] = -alt_m;
    t.pos_home_ned[0]    = distance_north_m;
    t.voltage_v          = 24.0f;
    t.r_internal_ohms    = 0.03f;
    t.energy_remaining_wh = 150.0f;
    return t;
}

/* 1. Симетричний штиль */
static void test_still_air(void) {
    printf("1. Штиль\n");
    return_budget_handle_t h;
    const return_config_t cfg = make_config();
    check(return_budget_init(&h, &cfg) == RETURN_OK, "ініціалізація");

    return_telemetry_t t = make_telemetry(2000.0f, 100.0f);
    return_budget_result_t r;
    const int32_t st = return_budget_update(&h, &t, 0.5f, &r);

    check(st == RETURN_OK, "розрахунок без помилки");
    check(approx(r.v_air_optimal_ms, cfg.v_best_range_still_ms, 1e-3f),
          "оптимальна швидкість = швидкість найкращої дальності");
    check(approx(r.time_to_home_sec, 2000.0f / 16.0f, 0.5f), "час повернення = D / V0");
    check(approx(r.wca_rad, 0.0f, 1e-4f), "кут випередження нульовий");
    check(r.e_climb_wh == 0.0f, "набирати висоту не треба");
    check(r.state == RETURN_STATE_OK && !r.rtl_mandatory, "стан OK");
}

/* 2. Штормовий зустрічний вітер */
static void test_storm_headwind(void) {
    printf("2. Зустрічний вітер 30 м/с\n");
    return_budget_handle_t h;
    const return_config_t cfg = make_config();
    return_budget_init(&h, &cfg);

    return_telemetry_t t = make_telemetry(2000.0f, 100.0f);
    t.wind_ned[0] = -30.0f;  /* повітря рухається на південь — точно в лоб */

    return_budget_result_t r;
    const int32_t st = return_budget_update(&h, &t, 0.5f, &r);

    check(st == RETURN_ERR_HEADWIND_TOO_HIGH, "виявлено неможливість повернення");
    check(approx(r.v_air_optimal_ms, cfg.v_air_max_ms, 1e-3f), "швидкість уперлась у стелю планера");
    check(r.v_ground_ret_ms <= 1.0f, "шляхова швидкість зближення втрачена");
    check(r.state == RETURN_STATE_EMERGENCY_LAND && r.rtl_mandatory, "аварійна посадка");
}

/* 3. Просідання напруги на виснаженій батареї */
static void test_voltage_sag(void) {
    printf("3. Залишок 25%%, R_int = 70 мОм\n");
    return_budget_handle_t h;
    const return_config_t cfg = make_config();
    return_budget_init(&h, &cfg);

    return_telemetry_t t = make_telemetry(2000.0f, 100.0f);
    t.voltage_v = 20.6f;
    t.r_internal_ohms = 0.070f;
    t.energy_remaining_wh = 0.25f * cfg.nominal_energy_wh;

    return_budget_result_t r;
    const int32_t st = return_budget_update(&h, &t, 0.5f, &r);
    const float v_cutoff = cfg.cell_count * cfg.cell_v_cutoff;

    check(st == RETURN_OK, "розрахунок без помилки");
    check(r.projected_sag_voltage_v < t.voltage_v, "прогноз напруги нижчий за поточну");
    check(r.projected_sag_voltage_v > v_cutoff, "до відсічки ще є запас");
    check(r.e_usable_compensated_wh < 0.9f * t.energy_remaining_wh,
          "недосяжний хвіст ємності відсічено");
}

/* 4. Порив вітру не має смикати тригер */
static void test_gust_filtering(void) {
    printf("4. Порив 0.5 с проти сталого вітру\n");
    return_budget_handle_t h;
    const return_config_t cfg = make_config();
    return_budget_init(&h, &cfg);

    return_telemetry_t calm = make_telemetry(20000.0f, 100.0f);
    calm.energy_remaining_wh = 105.0f;  /* запасу вистачає, але без надлишку */

    return_budget_result_t r;
    for (int i = 0; i < 20; ++i) {
        return_budget_update(&h, &calm, 0.5f, &r);
    }
    check(!r.rtl_mandatory, "усталений режим: повертатися ще не час");
    const float steady_wh = r.e_return_total_wh;

    return_telemetry_t gust = calm;
    gust.wind_ned[0] = -8.0f;  /* один кадр 0.5 с із зустрічним поривом */
    return_budget_update(&h, &gust, 0.5f, &r);

    check(!r.rtl_mandatory, "порив не викликав хибного RTL");
    check(r.e_return_total_wh > steady_wh, "оцінка все ж зросла — фільтр не глухий");

    /* Той самий вітер, але сталий: за кілька секунд тригер мусить спрацювати */
    for (int i = 0; i < 40; ++i) {
        return_budget_update(&h, &gust, 0.5f, &r);
    }
    check(r.rtl_mandatory, "сталий вітер довів оцінку до RTL");
}

/* 5. Боковий знос: asinf() не має віддати NaN */
static void test_crosswind_stall(void) {
    printf("5. Боковий вітер 16 м/с при швидкості 15 м/с\n");
    return_budget_handle_t h;
    return_config_t cfg = make_config();
    cfg.v_best_range_still_ms = 15.0f;
    cfg.v_air_max_ms = 15.0f;
    return_budget_init(&h, &cfg);

    return_telemetry_t t = make_telemetry(2000.0f, 100.0f);
    t.wind_ned[1] = 16.0f;  /* строго впоперек шляху додому */

    return_budget_result_t r;
    const int32_t st = return_budget_update(&h, &t, 0.5f, &r);

    check(st == RETURN_ERR_CROSSWIND_LIMIT, "повернуто RETURN_ERR_CROSSWIND_LIMIT");
    check(isfinite(r.v_air_optimal_ms) && isfinite(r.wca_rad), "у результаті немає NaN");
    check(r.state == RETURN_STATE_EMERGENCY_LAND && r.rtl_mandatory, "аварійна посадка");
}

int main(void) {
    test_still_air();
    test_storm_headwind();
    test_voltage_sag();
    test_gust_filtering();
    test_crosswind_stall();

    printf("\nневдалих перевірок: %d\n", g_failures);
    return g_failures == 0 ? 0 : 1;
}
