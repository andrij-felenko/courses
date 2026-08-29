// Калькулятор автономності польового вузла.
//
// Дані комірки взяті з даташиту літій-тіонілхлоридного елемента розміру A
// (2400 мА·год, плато 3.6 В), профіль споживання — з осцилограми реальної
// плати LoRaWAN. П'ять сценаріїв показують, як та сама плата з тією самою
// батареєю живе від чотирьох місяців до дванадцяти років — і в якому випадку
// вона не переживе навіть першої передачі.

#include "budget.hpp"
#include "cell.hpp"
#include "load_profile.hpp"

#include <format>
#include <iostream>
#include <string>
#include <vector>

namespace {

using namespace autonomy;
using namespace std::chrono_literals;

// ---------- даташит комірки ----------

Cell::Spec li_socl2_spec()
{
    return Cell::Spec{
        .name = "Li-SOCl2, розмір A",
        .capacity_mah = 2400.0,
        .ocv_fresh_v = 3.67,
        .reference_current_ma = 1.0,   // паспортну ємність міряли струмом 1 мА
        .r_int_20c_ohm = 0.50,
        .r_int_beta_k = 6300.0,        // дає ≈15 Ом за −20 °C
        .peukert_k = 1.08,
        .relax_time = Seconds{30.0},
        .self_discharge_pct_year = 1.5,
        .passivation_max_factor = 200.0,  // зріла плівка LiCl — сотні ом
        .passivation_onset = Days{730.0},
        // Розрядна крива Li-SOCl2: майже все віддається на плато 3.5–3.6 В,
        // тому кожні сто мілівольт порогу відсічки коштують дуже дорого.
        .curve = {{3.67, 0.00}, {3.62, 0.02}, {3.58, 0.20}, {3.55, 0.45}, {3.52, 0.70},
                  {3.48, 0.85}, {3.40, 0.93}, {3.20, 0.97}, {2.80, 0.99}, {2.00, 1.00}},
        .temperature = {{-40.0, 0.30}, {-20.0, 0.60}, {0.0, 0.85},
                        {20.0, 1.00}, {40.0, 1.00}, {60.0, 0.95}},
    };
}

// ---------- профілі споживання ----------

LoadProfile::Spec lora_node(Seconds period, bool depassivation)
{
    LoadProfile::Spec spec{
        .phases = {{"Пробудження й вимірювання", 8.0, 50ms},
                   {"Передача LoRa SF10", 45.0, 150ms},
                   {"Запис лічильника в EEPROM", 4.0, 10ms}},
        .sleep_current_ma = 0.005,
        .period = period,
    };
    if (depassivation) {
        spec.depassivation = Phase{"Депасиваційний імпульс", 8.0, 30ms};
        spec.depassivation_period = Days{1};
    }
    return spec;
}

LoadProfile::Spec nbiot_node(Seconds period)
{
    return LoadProfile::Spec{
        .phases = {{"Пробудження й вимірювання", 12.0, 80ms},
                   {"Реєстрація й сеанс NB-IoT", 250.0, 1800ms},
                   {"Запис лічильника в EEPROM", 4.0, 10ms}},
        .sleep_current_ma = 0.008,
        .period = period,
    };
}

struct Scenario {
    std::string title;
    LoadProfile::Spec load;
    Site site;
};

std::vector<Scenario> scenarios()
{
    return {
        {"Кімнатна температура, передача щохвилини",
         lora_node(Seconds{60.0}, true),
         {.cutoff_v = 2.90, .temp_c = 20.0, .storage = Days{30.0}, .safety_factor = 0.80}},

        {"Мороз −20 °C, той самий вузол і той самий цикл",
         lora_node(Seconds{60.0}, true),
         {.cutoff_v = 2.90, .temp_c = -20.0, .storage = Days{30.0}, .safety_factor = 0.80}},

        {"Ящик на сонці +50 °C, передача раз на 10 хвилин",
         lora_node(Seconds{600.0}, true),
         {.cutoff_v = 2.90, .temp_c = 50.0, .storage = Days{30.0}, .safety_factor = 0.80}},

        {"Два роки на складі: перший імпульс після пасивації",
         lora_node(Seconds{600.0}, false),
         {.cutoff_v = 2.90, .temp_c = 20.0, .storage = Days{730.0}, .safety_factor = 0.80}},

        {"NB-IoT на морозі: 250 мА в пік, поріг модема 3.1 В",
         nbiot_node(Seconds{900.0}),
         {.cutoff_v = 3.10, .temp_c = -20.0, .storage = Days{30.0}, .safety_factor = 0.80}},
    };
}

// ---------- друк звіту ----------
//
// std::format міряє ширину поля в символах, а не в байтах, тож кирилиця в
// колонках не роз'їжджається — на відміну від printf, якому довелося б
// рахувати UTF-8 руками.

void rule(char c)
{
    std::cout << std::string(74, c) << '\n';
}

void print_waterfall(const Cell& cell, const Site& site, const Estimate& est)
{
    std::cout << "ВОДОСПАД ЄМНОСТІ\n";
    std::cout << std::format("  {:<46}{:>9.1f} мА·год\n", "паспортна ємність", cell.capacity_mah());
    std::cout << std::format("  × η_cutoff = {:.3f} (поріг {:.2f} В + просадка {:.2f} В)\n",
                             est.eta_cutoff, site.cutoff_v, est.pulse.sag_v);
    std::cout << std::format("    {:<44}{:>9.1f} мА·год\n", "доступно за напругою", est.c_after_cutoff_mah);
    std::cout << std::format("  × η_temp   = {:.3f} ({:+.0f} °C)\n", est.eta_temp, site.temp_c);
    std::cout << std::format("    {:<44}{:>9.1f} мА·год\n", "доступно за температурою", est.c_after_temp_mah);
    std::cout << std::format("  × η_pulse  = {:.3f} (пік {:.1f} мА, спокій {:.0f} с)\n",
                             est.eta_pulse, est.load.peak_current_ma, est.load.rest.count());
    std::cout << std::format("  {:<46}{:>9.1f} мА·год  ({:.1f} % паспорта)\n", "ФАКТИЧНО ДОСТУПНО",
                             est.c_eff_mah, 100.0 * est.c_eff_mah / cell.capacity_mah());
}

void print_phases(const Load& load, const Site& site)
{
    std::cout << std::format("ЗАРЯД ЗА ЦИКЛ (період {:.0f} с, температура {:+.0f} °C)\n",
                             load.period.count(), site.temp_c);
    std::cout << std::format("  {:<30}{:>9}{:>10}{:>11}{:>9}    {}\n", "фаза", "I, мА", "t, мс", "Q, мА·с",
                             "частка", "Пейкерт");

    for (const PhaseShare& share : load.shares) {
        std::cout << std::format("  {:<30}{:>9.3f}{:>10.1f}{:>11.3f}{:>9.1f} %  ×{:.3f}\n", share.name,
                                 share.current_ma, share.duration.count() * 1000.0, share.charge_mas,
                                 share.share * 100.0, share.peukert_cost);
    }
    std::cout << std::format("  {:<30}{:>9}{:>10}{:>11.3f}{:>9.1f} %\n", "разом за цикл", "", "",
                             load.q_cycle_mas, 100.0);
}

void print_currents(const Cell& cell, const Site& site, const Estimate& est)
{
    constexpr double kHoursPerYear = 8766.0;

    std::cout << "СТРУМИ\n";
    std::cout << std::format("  {:<46}{:>9.2f} мкА\n", "середній струм навантаження", est.i_avg_ma * 1000.0);
    std::cout << std::format("  {:<46}{:>9.2f} мкА  ({:.2f} %/рік за {:+.0f} °C)\n",
                             "еквівалентний струм саморозряду", est.i_self_ma * 1000.0,
                             100.0 * est.i_self_ma * kHoursPerYear / cell.capacity_mah(), site.temp_c);
    std::cout << std::format("  {:<46}{:>9.2f} мкА\n", "разом", est.i_total_ma * 1000.0);
}

void print_pulse(const Site& site, const Estimate& est)
{
    const PulseCheck& pulse = est.pulse;

    std::cout << "ІМПУЛЬС ПЕРЕДАВАЧА\n";
    std::cout << std::format("  внутрішній опір за {:+.0f} °C: {:.2f} Ом\n", site.temp_c, pulse.r_int_ohm);
    std::cout << std::format("  просадка {:.1f} мА · {:.2f} Ом = {:.2f} В → на клемах {:.2f} В "
                             "(поріг {:.2f} В)  {}\n",
                             est.load.peak_current_ma, pulse.r_int_ohm, pulse.sag_v, pulse.v_term_v,
                             site.cutoff_v, pulse.brownout ? "✖ СКИДАННЯ" : "гаразд");
    std::cout << std::format("  після {:.0f} діб спокою опір {:.1f} Ом → на клемах {:.2f} В  {}\n",
                             site.storage.count(), pulse.r_passivated_ohm, pulse.v_term_storage_v,
                             pulse.brownout_after_storage ? "✖ СКИДАННЯ" : "гаразд");

    if (pulse.buffer_impossible) {
        std::cout << "  ✖ поріг відсічки вищий за робоче плато комірки — буфер не врятує,\n"
                     "    треба інша хімія, нижчий поріг або менший піковий струм\n";
        return;
    }
    if (!pulse.buffer) {
        std::cout << "  буфер не потрібен: імпульс укладається в бюджет напруги\n";
        return;
    }
    std::cout << std::format("  потрібен буфер ≥ {:.0f} мкФ з ESR ≤ {:.2f} Ом (запас {:.2f} В)\n",
                             pulse.buffer->farads * 1.0e6, pulse.buffer->esr_max_ohm, pulse.headroom_v);
    std::cout << (pulse.buffer->hybrid_needed
                      ? "  керамікою й танталом стільки не набрати — потрібен гібридний шар (HLC)\n"
                      : "  вистачить банку танталових конденсаторів із низьким ESR\n");
}

void print_lifetime(const Site& site, const Estimate& est)
{
    std::cout << "ЧАС АВТОНОМНОСТІ\n";
    std::cout << std::format("  {:<46}{:>9.2f} року\n", "наївна оцінка (паспорт / I_avg)", est.naive.count());

    if (est.c_eff_mah <= 0.0 || est.life_years <= Years{0}) {
        std::cout << "  реальна оцінка: 0 — пристрій не працює за цих умов\n";
    } else {
        std::cout << std::format("  {:<46}{:>9.2f} року  ({:.0f} діб, {:.0f} год)\n", "реальна оцінка",
                                 est.life_years.count(), Days{est.life}.count(), est.life.count());
        std::cout << std::format("  {:<46}{:>9.2f} року  (k_safe = {:.2f})\n", "з інженерним запасом",
                                 est.guaranteed.count(), site.safety_factor);
        std::cout << std::format("  наївний розрахунок завищений у {:.1f} раза\n", est.optimism_ratio);
    }
    std::cout << std::format("  обмежувач: {} — {}\n", describe(est.limiter), est.limiter_note);
}

void run(const Cell& cell, const Scenario& scenario)
{
    rule('=');
    std::cout << std::format("СЦЕНАРІЙ: {}\n", scenario.title);
    std::cout << std::format("Комірка: {}, {:.0f} мА·год · відсічка {:.2f} В · запас {:.2f}\n", cell.name(),
                             cell.capacity_mah(), scenario.site.cutoff_v, scenario.site.safety_factor);
    rule('-');

    const auto profile = LoadProfile::create(scenario.load);
    if (!profile) {
        std::cout << std::format("✖ профіль неприйнятний: {}\n\n", describe(profile.error()));
        return;
    }

    const auto est = estimate(cell, *profile, scenario.site);
    if (!est) {
        std::cout << std::format("✖ розрахунок неможливий: {}\n\n", describe(est.error()));
        return;
    }

    print_waterfall(cell, scenario.site, *est);
    rule('-');
    print_phases(est->load, scenario.site);
    rule('-');
    print_currents(cell, scenario.site, *est);
    rule('-');
    print_pulse(scenario.site, *est);
    rule('-');
    print_lifetime(scenario.site, *est);
    std::cout << '\n';
}

}  // namespace

int main()
{
    const auto cell = Cell::create(li_socl2_spec());
    if (!cell) {
        std::cerr << std::format("✖ даташит комірки описано неправильно: {}\n", describe(cell.error()));
        return 1;
    }

    for (const Scenario& scenario : scenarios()) {
        run(*cell, scenario);
    }
    return 0;
}
