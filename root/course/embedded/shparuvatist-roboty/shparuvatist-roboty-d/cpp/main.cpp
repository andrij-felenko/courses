// Розрахунок робочої точки автономного вузла: профіль споживання,
// обернена задача під цільовий термін служби, крива насичення
// й перевірка годинного ліміту часу в ефірі.

#include "duty_model.hpp"
#include "radio_band.hpp"

#include <array>
#include <format>
#include <initializer_list>
#include <iostream>
#include <string>

namespace {

// Приклад зі статті: I_on = 60 мА, t_on = 10 мс, I_sleep = 3 мкА → T_sat ≈ 30 хв.
// Модель constexpr, тож число перевіряє компілятор, а не запуск програми.
constexpr duty::Config article_example{
    .active_current_ua = 60'000.0,
    .active_window = duty::seconds_f{0.010},
    .sleep_current_ua = 3.0,
    .period = duty::seconds_f{600.0},
    .capacity_mah = 1000.0,
};
static_assert(duty::evaluate(article_example).has_value());
static_assert(duty::evaluate(article_example)->saturation_period > duty::seconds_f{1799.0});
static_assert(duty::evaluate(article_example)->saturation_period < duty::seconds_f{1801.0});

std::string as_minutes(duty::seconds_f t) {
    if (t.count() > 1e12)  // без витоків насичення не настає ніколи
        return "ніколи";
    return t.count() >= 3600.0
        ? std::format("{:.0f} с ({:.1f} год)", t.count(), t.count() / 3600.0)
        : std::format("{:.0f} с ({:.1f} хв)", t.count(), t.count() / 60.0);
}

void show(const duty::Config& cfg, const duty::Profile& p) {
    const auto t_on_ms = std::chrono::duration<double, std::milli>(cfg.active_window);
    std::cout << std::format(
        "Робоча точка: T = {:.0f} с, t_on = {:.0f} мс, I_on = {:.0f} мкА, I_sleep = {:.1f} мкА\n"
        "  шпаруватість D    : {:.7f} ({:.5f} %)\n"
        "  середній струм    : {:.2f} мкА\n"
        "  заряд за цикл     : активний {:.0f} мкА·с, сон {:.0f} мкА·с (k = {:.2f})\n"
        "  розподіл заряду   : спалах {:.1f} %, сон {:.1f} %\n"
        "  автономність      : {:.0f} год ({:.1f} років)\n"
        "  рівновага k = 1   : {}\n"
        "  насичення T_90    : {}\n",
        cfg.period.count(), t_on_ms.count(), cfg.active_current_ua, cfg.sleep_current_ua,
        p.duty, p.duty * 100.0,
        p.avg_current_ua,
        p.active_charge_uas, p.sleep_charge_uas, p.energy_ratio,
        p.active_share() * 100.0, p.sleep_share() * 100.0,
        p.lifetime.count(), p.lifetime_years().count(),
        as_minutes(p.equilibrium_period), as_minutes(p.saturation_period));
}

void show_airtime(const radio::Band& band, duty::seconds_f toa, duty::seconds_f period) {
    const auto b = radio::budget(band, toa, period);
    if (!b) {
        std::cerr << std::format("Бюджет ефіру не порахувати: {}\n", duty::describe(b.error()));
        return;
    }
    std::cout << std::format(
        "\nETSI {} ({:.2f}–{:.2f} МГц, D <= {:.1f} %, до {:+.0f} дБм); пакет {:.2f} с, період {:.0f} с\n"
        "  дозволено за годину : {:.1f} с\n"
        "  фактично за годину  : {:.1f} с ({:.0f} % ліміту)\n"
        "  один пакет з'їдає   : {:.2f} % бюджету, за годину влізе {:.0f} штук\n"
        "  мінімальний період  : {:.0f} с — {}\n",
        band.name, band.lo_mhz, band.hi_mhz, band.duty_limit * 100.0, band.max_erp_dbm,
        toa.count(), period.count(),
        b->allowance.count(), b->used.count(), b->utilisation * 100.0,
        b->packet_share * 100.0, b->packets_allowed(),
        b->min_period.count(),
        b->compliant() ? "ліміт дотримано" : "стек заблокує вихід в ефір");
}

} // namespace

int main() {
    // Вузол LoRaWAN зі статті: елемент Li-SOCl2 типорозміру AA,
    // спалах 30 мс при 40 мА, виміряний струм спокою плати 2.8 мкА.
    constexpr duty::Config node{
        .active_current_ua = 40'000.0,
        .active_window = duty::seconds_f{0.030},
        .sleep_current_ua = 2.8,
        .period = duty::seconds_f{600.0},
        .capacity_mah = 2600.0,
        .derating = 0.85,
    };

    const auto profile = duty::evaluate(node);
    if (!profile) {
        std::cerr << std::format("Профіль неспроможний: {}\n", duty::describe(profile.error()));
        return 1;
    }
    show(node, *profile);

    // Обернена задача: під який період вузол дотягує рівно до 5 років.
    if (const auto t_min = duty::min_period(node, duty::years_f{5.0}); t_min)
        std::cout << std::format("\nМінімальний період для 5 років: {:.1f} с ({:.1f} хв)\n",
                                 t_min->count(), t_min->count() / 60.0);
    else
        std::cout << std::format("\n5 років недосяжні: {}\n", duty::describe(t_min.error()));

    // Та сама вимога, але плата з паразитним витоком: період уже не рятує.
    duty::Config leaky = node;
    leaky.sleep_current_ua = 60.0;
    const auto leaky_period = duty::min_period(leaky, duty::years_f{5.0});
    std::cout << std::format("Плата з витоком 60 мкА: {}\n",
                             leaky_period ? std::format("період {:.0f} с", leaky_period->count())
                                          : std::string{duty::describe(leaky_period.error())});

    // Скан періодів: видно, як крива лягає на плато I_sleep.
    constexpr std::array<duty::seconds_f, 7> scan{{
        duty::seconds_f{10.0},   duty::seconds_f{60.0},    duty::seconds_f{300.0},
        duty::seconds_f{1800.0}, duty::seconds_f{3600.0},  duty::seconds_f{21600.0},
        duty::seconds_f{86400.0},
    }};
    std::cout << "\n     T, с           D   I_avg, мкА     роки   сон, %\n";
    for (const auto period : scan) {
        duty::Config probe = node;
        probe.period = period;
        const auto p = duty::evaluate(probe);
        if (!p) {
            std::cerr << std::format("T = {:.0f} с: {}\n", period.count(), duty::describe(p.error()));
            continue;
        }
        std::cout << std::format("{:9.0f}  {:10.7f}   {:10.2f}  {:7.1f}  {:7.1f}{}\n",
                                 period.count(), p->duty, p->avg_current_ua,
                                 p->lifetime_years().count(), p->sleep_share() * 100.0,
                                 period >= profile->saturation_period
                                     ? "   <- за точкою насичення" : "");
    }

    // Регулятор: довгий пакет SF12 тривалістю 1.48 с у смузі g1.
    constexpr auto g1 = radio::band_for(868.1);
    static_assert(g1.has_value(), "868.1 МГц мусить потрапляти в g1");
    constexpr duty::seconds_f toa_sf12{1.48};

    for (const auto period : {node.period, duty::seconds_f{60.0}})
        show_airtime(*g1, toa_sf12, period);

    return 0;
}
