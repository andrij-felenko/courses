#pragma once

// Профіль споживання: інтегрування заряду за фазами робочого циклу.
//
// Те саме, що робить осцилограф зі струмовим шунтом: складає заряд усіх фаз,
// ділить на період і каже, хто саме з'їв заряд. Сон окремої фази не має —
// він триває стільки, скільки лишилося від періоду після всіх пробуджень.

#include "cell.hpp"

#include <chrono>
#include <expected>
#include <optional>
#include <string>
#include <vector>

namespace autonomy {

struct Phase {
    std::string name;
    double current_ma{};
    std::chrono::milliseconds duration{};
};

enum class PhaseKind { Active, Sleep, Depassivation };

// Внесок однієї фази в заряд циклу.
struct PhaseShare {
    std::string name;
    double current_ma{};
    Seconds duration{};
    double charge_mas{};    // заряд за цикл, мА·с
    double share{};         // частка від заряду циклу
    double peukert_cost{};  // у скільки разів дорожче обійшовся цей заряд
    PhaseKind kind{PhaseKind::Active};
};

struct Load {
    Seconds active{};
    Seconds rest{};              // скільки комірка відпочиває між пробудженнями
    Seconds period{};
    double q_active_mas{};       // Q_active — неподільний заряд одного пробудження
    double q_cycle_mas{};        // Q_cycle
    double q_cycle_peukert_mas{};
    double eta_pulse{};          // Q_cycle / Q_cycle_peukert
    double i_avg_ma{};           // I_avg = Q_cycle / T_period
    double peak_current_ma{};
    Seconds peak_duration{};
    std::string peak_phase;
    std::vector<PhaseShare> shares;  // активні фази, сон і депасивація
};

class LoadProfile {
public:
    struct Spec {
        std::vector<Phase> phases;       // активні фази одного пробудження
        double sleep_current_ma{};       // разом зі струмом спокою стабілізатора
        Seconds period{};                // T_period
        // Депасиваційний імпульс: помірне навантаження раз на добу, щоб плівка
        // LiCl не встигала зростати. Порожньо — процедури немає.
        std::optional<Phase> depassivation{};
        Seconds depassivation_period{Days{1}};
    };

    static std::expected<LoadProfile, Error> create(Spec spec);

    std::expected<Load, Error> analyse(const Cell& cell) const;

    const Spec& spec() const noexcept { return spec_; }

private:
    explicit LoadProfile(Spec spec) noexcept : spec_{std::move(spec)} {}

    Spec spec_;
};

}  // namespace autonomy
