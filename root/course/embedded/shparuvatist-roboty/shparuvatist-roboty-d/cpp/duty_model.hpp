#pragma once
// Модель шпаруватості автономного вузла.
//
// Уся арифметика constexpr: робочу точку рахують ще під час компіляції
// прошивки, а static_assert у місці виклику ловить неспроможну конфігурацію
// до того, як плата поїде на об'єкт. Час — типами <chrono>, помилки —
// std::expected: сплутати секунди з мілісекундами тут нема як.

#include <chrono>
#include <expected>
#include <limits>
#include <ratio>
#include <string_view>

namespace duty {

using seconds_f = std::chrono::duration<double>;
using hours_f   = std::chrono::duration<double, std::ratio<3600>>;
using years_f   = std::chrono::duration<double, std::ratio<31'557'600>>; // 365.25 доби

struct Config {
    double    active_current_ua{};  // I_on, мкА
    seconds_f active_window{};      // t_on
    double    sleep_current_ua{};   // I_sleep, мкА
    seconds_f period{};             // T
    double    capacity_mah{};       // номінальна ємність джерела
    double    derating{0.85};       // коефіцієнт корисної віддачі ємності
};

struct Profile {
    double    duty{};                // D = t_on / T
    double    avg_current_ua{};      // I_avg
    double    active_charge_uas{};   // Q_on
    double    sleep_charge_uas{};    // Q_off
    double    energy_ratio{};        // k = Q_off / Q_on
    hours_f   lifetime{};
    seconds_f equilibrium_period{};  // k = 1
    seconds_f saturation_period{};   // k = 9, вона ж T_90

    [[nodiscard]] constexpr double active_share() const noexcept {
        return active_charge_uas / (active_charge_uas + sleep_charge_uas);
    }
    [[nodiscard]] constexpr double sleep_share() const noexcept {
        return 1.0 - active_share();
    }
    [[nodiscard]] constexpr years_f lifetime_years() const noexcept {
        return years_f{lifetime};
    }
};

enum class Error {
    BadPeriod,    // період не додатний або NaN
    BadWindow,    // активне вікно порожнє чи довше за період
    BadCurrent,   // порушено 0 <= I_sleep < I_on
    BadBattery,   // ємність або віддача поза межами
    BadTarget,    // цільовий термін служби не додатний
    Unreachable   // мети не досягти за жодного періоду
};

[[nodiscard]] constexpr std::string_view describe(Error e) noexcept {
    switch (e) {
        case Error::BadPeriod:   return "період циклу мусить бути додатним";
        case Error::BadWindow:   return "активне вікно порожнє або довше за період";
        case Error::BadCurrent:  return "очікуємо 0 <= I_sleep < I_on";
        case Error::BadBattery:  return "ємність або коефіцієнт віддачі поза межами";
        case Error::BadTarget:   return "цільовий термін служби мусить бути додатним";
        case Error::Unreachable: return "мети не досягти: сам струм спокою вичерпає джерело";
    }
    return "невідома помилка";
}

namespace detail {

// Порівняння навмисно заперечені: NaN із недовиміряного лога споживання
// провалює перевірку, а не прослизає далі й не отруює похідні числа.
[[nodiscard]] constexpr std::expected<void, Error> validate(const Config& cfg) noexcept {
    if (!(cfg.period > seconds_f::zero()))
        return std::unexpected(Error::BadPeriod);
    if (!(cfg.active_window > seconds_f::zero()) || cfg.active_window > cfg.period)
        return std::unexpected(Error::BadWindow);
    if (!(cfg.sleep_current_ua >= 0.0) || !(cfg.active_current_ua > cfg.sleep_current_ua))
        return std::unexpected(Error::BadCurrent);
    if (!(cfg.capacity_mah > 0.0) || !(cfg.derating > 0.0) || cfg.derating > 1.0)
        return std::unexpected(Error::BadBattery);
    return {};
}

// Ефективна ємність у мкА·год: номінал за відрахуванням саморозряду,
// просідання на внутрішньому опорі й морозу.
[[nodiscard]] constexpr double effective_capacity_uah(const Config& cfg) noexcept {
    return cfg.capacity_mah * cfg.derating * 1000.0;
}

} // namespace detail

// Пряма задача: профіль споживання за конфігурацією циклу.
[[nodiscard]] constexpr std::expected<Profile, Error> evaluate(const Config& cfg) noexcept {
    if (const auto ok = detail::validate(cfg); !ok)
        return std::unexpected(ok.error());

    const double t_on  = cfg.active_window.count();
    const double t_all = cfg.period.count();
    const double t_off = t_all - t_on;

    Profile p{};
    p.duty = t_on / t_all;
    p.active_charge_uas = cfg.active_current_ua * t_on;
    p.sleep_charge_uas  = cfg.sleep_current_ua * t_off;

    // I_avg = (I_on·t_on + I_sleep·t_off) / T — зважена сума, а не струм радіо.
    const double q_total = p.active_charge_uas + p.sleep_charge_uas;
    p.avg_current_ua = q_total / t_all;
    p.energy_ratio   = p.sleep_charge_uas / p.active_charge_uas;
    p.lifetime = hours_f{detail::effective_capacity_uah(cfg) / p.avg_current_ua};

    // Розв'язок I_sleep·(T − t_on) = k·I_on·t_on точний; формула статті
    // T = k·(I_on/I_sleep)·t_on нехтує доданком t_on, і при D << 1
    // різниця між ними — соті частки відсотка.
    if (cfg.sleep_current_ua > 0.0) {
        const double ratio = cfg.active_current_ua / cfg.sleep_current_ua;
        p.equilibrium_period = seconds_f{t_on * (1.0 + ratio)};
        p.saturation_period  = seconds_f{t_on * (1.0 + 9.0 * ratio)};
    } else {
        // Ідеального нуля витоків не буває, але модель мусить його пережити:
        // без струму спокою сон ніколи не переважить спалах.
        constexpr double inf = std::numeric_limits<double>::infinity();
        p.equilibrium_period = seconds_f{inf};
        p.saturation_period  = seconds_f{inf};
    }
    return p;
}

// Обернена задача: найкоротший період, за якого вузол ще дотягує до target.
[[nodiscard]] constexpr std::expected<seconds_f, Error>
min_period(const Config& cfg, years_f target) noexcept {
    if (const auto ok = detail::validate(cfg); !ok)
        return std::unexpected(ok.error());
    if (!(target > years_f::zero()))
        return std::unexpected(Error::BadTarget);

    const hours_f budget{target};
    const double i_avg_max = detail::effective_capacity_uah(cfg) / budget.count();

    // Асимптота закону: I_avg прямує до I_sleep, а не до нуля.
    if (i_avg_max <= cfg.sleep_current_ua)
        return std::unexpected(Error::Unreachable);
    // Бюджету стачає навіть на безперервну роботу — сон не потрібен.
    if (i_avg_max >= cfg.active_current_ua)
        return cfg.active_window;

    const double t_on = cfg.active_window.count();
    return seconds_f{(cfg.active_current_ua - cfg.sleep_current_ua) * t_on
                     / (i_avg_max - cfg.sleep_current_ua)};
}

} // namespace duty
