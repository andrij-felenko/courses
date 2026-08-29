// Польотні сценарії з розділу «Верифікація». Збірка на хості:
//   c++ -std=c++23 -O2 -I../include -o tests return_budget_tests.cpp ../src/return_budget.cpp
#include "uav/return_budget.hpp"

#include <cmath>
#include <cstdio>
#include <string_view>

namespace {

using uav::nav::Budget;
using uav::nav::Config;
using uav::nav::Error;
using uav::nav::Estimator;
using uav::nav::State;
using uav::nav::Telemetry;

int g_failures = 0;

void check(bool ok, std::string_view what) {
    std::printf("  %s %.*s\n", ok ? "[ok]" : "[FAIL]",
                static_cast<int>(what.size()), what.data());
    if (!ok) ++g_failures;
}

bool approx(float a, float b, float eps) {
    return std::abs(a - b) <= eps;
}

// Планер із розділу 3: калібрована поляра й 6S-пакет
Config makeConfig() {
    return Config{.v_air_min_ms = 12.0f,
                  .v_air_max_ms = 28.0f,
                  .v_best_range_still_ms = 16.0f,
                  .c_ind = 1500.0f,
                  .c_par = 0.02f,
                  .p_avionics_watts = 12.0f,
                  .rtl_safe_altitude_m = 80.0f,
                  .v_climb_ms = 3.0f,
                  .p_climb_watts = 450.0f,
                  .p_hover_watts = 900.0f,
                  .t_land_maneuver_sec = 25.0f,
                  .reserve_margin_ratio = 0.25f,
                  .filter_time_constant_s = 8.0f,
                  .nominal_energy_wh = 220.0f,
                  .cell_v_cutoff = 3.3f,
                  .cell_count = 6};
}

// База на північ від борту, штиль, пакет здоровий
Telemetry makeTelemetry(float distance_north_m, float altitude_m) {
    Telemetry t{};
    t.position = {.north = 0.0f, .east = 0.0f, .down = -altitude_m};
    t.home = {.north = distance_north_m, .east = 0.0f, .down = 0.0f};
    t.voltage_v = 24.0f;
    t.r_internal_ohms = 0.03f;
    t.energy_remaining_wh = 150.0f;
    return t;
}

// 1. Симетричний штиль
void testStillAir() {
    std::printf("1. Штиль\n");
    const Config cfg = makeConfig();
    auto estimator = Estimator::create(cfg);
    check(estimator.has_value(), "оцінювач створено");
    if (!estimator) return;

    const auto budget = estimator->update(makeTelemetry(2000.0f, 100.0f), 0.5f);
    check(budget.has_value(), "розрахунок без помилки");
    if (!budget) return;

    check(approx(budget->v_air_optimal_ms, cfg.v_best_range_still_ms, 1e-3f),
          "оптимальна швидкість = швидкість найкращої дальності");
    check(approx(budget->time_to_home_sec, 2000.0f / 16.0f, 0.5f), "час повернення = D / V0");
    check(approx(budget->wca_rad, 0.0f, 1e-4f), "кут випередження нульовий");
    check(budget->e_climb_wh == 0.0f, "набирати висоту не треба");
    check(budget->state == State::Ok && !budget->rtl_mandatory, "стан OK");
}

// 2. Штормовий зустрічний вітер
void testStormHeadwind() {
    std::printf("2. Зустрічний вітер 30 м/с\n");
    auto estimator = Estimator::create(makeConfig());
    if (!estimator) return;

    Telemetry t = makeTelemetry(2000.0f, 100.0f);
    t.wind.north = -30.0f;  // повітря рухається на південь — точно в лоб

    const auto budget = estimator->update(t, 0.5f);
    check(!budget.has_value(), "повернення визнано неможливим");
    check(budget.error() == Error::HeadwindTooHigh, "код помилки HeadwindTooHigh");
    check(estimator->state() == State::EmergencyLand, "оцінювач перейшов у аварійну посадку");
}

// 3. Просідання напруги на виснаженій батареї
void testVoltageSag() {
    std::printf("3. Залишок 25%%, R_int = 70 мОм\n");
    const Config cfg = makeConfig();
    auto estimator = Estimator::create(cfg);
    if (!estimator) return;

    Telemetry t = makeTelemetry(2000.0f, 100.0f);
    t.voltage_v = 20.6f;
    t.r_internal_ohms = 0.070f;
    t.energy_remaining_wh = 0.25f * cfg.nominal_energy_wh;

    const auto budget = estimator->update(t, 0.5f);
    check(budget.has_value(), "розрахунок без помилки");
    if (!budget) return;

    const float cutoff_v = static_cast<float>(cfg.cell_count) * cfg.cell_v_cutoff;
    check(budget->projected_sag_voltage_v < t.voltage_v, "прогноз напруги нижчий за поточну");
    check(budget->projected_sag_voltage_v > cutoff_v, "до відсічки ще є запас");
    check(budget->e_usable_compensated_wh < 0.9f * t.energy_remaining_wh,
          "недосяжний хвіст ємності відсічено");
}

// 4. Порив вітру не має смикати тригер
void testGustFiltering() {
    std::printf("4. Порив 0.5 с проти сталого вітру\n");
    auto estimator = Estimator::create(makeConfig());
    if (!estimator) return;

    Telemetry calm = makeTelemetry(20000.0f, 100.0f);
    calm.energy_remaining_wh = 105.0f;  // запасу вистачає, але без надлишку

    float steady_wh = 0.0f;
    bool steady_ok = true;
    for (int i = 0; i < 20; ++i) {
        const auto budget = estimator->update(calm, 0.5f);
        if (!budget) { steady_ok = false; break; }
        steady_wh = budget->e_return_total_wh;
        steady_ok = !budget->rtl_mandatory;
    }
    check(steady_ok, "усталений режим: повертатися ще не час");

    Telemetry gust = calm;
    gust.wind.north = -8.0f;  // один кадр 0.5 с із зустрічним поривом

    const auto gusted = estimator->update(gust, 0.5f);
    check(gusted.has_value(), "порив не зламав розрахунок");
    if (!gusted) return;
    check(!gusted->rtl_mandatory, "порив не викликав хибного RTL");
    check(gusted->e_return_total_wh > steady_wh, "оцінка все ж зросла — фільтр не глухий");

    // Той самий вітер, але сталий: за кілька секунд тригер мусить спрацювати
    bool mandatory = false;
    for (int i = 0; i < 40; ++i) {
        const auto budget = estimator->update(gust, 0.5f);
        if (budget) mandatory = budget->rtl_mandatory;
    }
    check(mandatory, "сталий вітер довів оцінку до RTL");
}

// 5. Боковий знос: std::asin не має віддати NaN
void testCrosswindStall() {
    std::printf("5. Боковий вітер 16 м/с при швидкості 15 м/с\n");
    Config cfg = makeConfig();
    cfg.v_best_range_still_ms = 15.0f;
    cfg.v_air_max_ms = 15.0f;

    auto estimator = Estimator::create(cfg);
    if (!estimator) return;

    Telemetry t = makeTelemetry(2000.0f, 100.0f);
    t.wind.east = 16.0f;  // строго впоперек шляху додому

    const auto budget = estimator->update(t, 0.5f);
    check(!budget.has_value(), "розрахунок перервано, а не віддано NaN");
    check(budget.error() == Error::CrosswindLimit, "код помилки CrosswindLimit");
    check(estimator->state() == State::EmergencyLand, "аварійна посадка");
}

} // namespace

int main() {
    testStillAir();
    testStormHeadwind();
    testVoltageSag();
    testGustFiltering();
    testCrosswindStall();

    std::printf("\nневдалих перевірок: %d\n", g_failures);
    return g_failures == 0 ? 0 : 1;
}
