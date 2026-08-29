#pragma once
// Регуляторний бік шпаруватості: годинний ліміт часу в ефірі для
// безліцензійних піддіапазонів EU868 (ETSI EN 300 220). Таблиця constexpr,
// тож приналежність частоти до смуги перевіряє компілятор.

#include <array>
#include <chrono>
#include <cmath>
#include <expected>
#include <optional>
#include <string_view>

#include "duty_model.hpp"

namespace radio {

using duty::seconds_f;

struct Band {
    std::string_view name;
    double lo_mhz{};
    double hi_mhz{};
    double duty_limit{};   // частка години: 0.01 = 1 %
    double max_erp_dbm{};

    [[nodiscard]] constexpr seconds_f hourly_allowance() const noexcept {
        return seconds_f{3600.0 * duty_limit};
    }
    [[nodiscard]] constexpr bool covers(double mhz) const noexcept {
        return mhz >= lo_mhz && mhz <= hi_mhz;
    }
};

inline constexpr std::array<Band, 3> eu868{{
    {"g1", 868.00, 868.60, 0.010, 14.0},  // основний LoRaWAN, 36 с/год
    {"g2", 868.70, 869.20, 0.001, 14.0},  // 3.6 с/год
    {"g3", 869.40, 869.65, 0.100, 27.0},  // шлюзи, 6 хв/год
}};

[[nodiscard]] constexpr std::optional<Band> band_for(double mhz) noexcept {
    for (const Band& b : eu868)
        if (b.covers(mhz))
            return b;
    return std::nullopt; // частота поза сіткою EU868 — судити нема за чим
}

struct AirtimeBudget {
    seconds_f allowance{};      // дозволено за годину
    seconds_f used{};           // фактично за годину
    double utilisation{};       // used / allowance
    double packet_share{};      // яку частку ліміту з'їдає один пакет
    double packets_per_hour{};  // скільки таких пакетів дозволяє смуга
    seconds_f min_period{};     // мінімальний період за регулятором

    [[nodiscard]] constexpr bool compliant() const noexcept { return used <= allowance; }
    [[nodiscard]] double packets_allowed() const noexcept { return std::floor(packets_per_hour); }
};

// time_on_air — час випромінювання ОДНОГО пакета, не все активне вікно:
// регулятор рахує ефір, а не пробудження й обчислення.
[[nodiscard]] constexpr std::expected<AirtimeBudget, duty::Error>
budget(const Band& band, seconds_f time_on_air, seconds_f period) noexcept {
    if (!(time_on_air > seconds_f::zero()))
        return std::unexpected(duty::Error::BadWindow);
    if (!(period > seconds_f::zero()))
        return std::unexpected(duty::Error::BadPeriod);

    const double sessions_per_hour = 3600.0 / period.count();

    AirtimeBudget b{};
    b.allowance = band.hourly_allowance();
    b.used = time_on_air * sessions_per_hour;
    b.utilisation = b.used / b.allowance;
    b.packet_share = time_on_air / b.allowance;
    b.packets_per_hour = b.allowance / time_on_air;
    b.min_period = time_on_air / band.duty_limit;
    return b;
}

} // namespace radio
