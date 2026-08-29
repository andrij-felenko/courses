#pragma once

// Книга витрат заряду за фазами циклу.
//
// Тривалості приходять як std::chrono::microseconds, а не як «число, що,
// напевно, у мікросекундах»: переплутати секунди з мілісекундами тут просто
// не вийде, компілятор перерахує сам.

#include "budget/flags.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace budget {

enum class Phase : std::size_t { Sleep = 0, Sense, Process, Transmit };

inline constexpr std::size_t kPhaseCount = 4;

using Microamps = std::uint32_t;

class EnergyLedger {
public:
    using Clock   = std::chrono::steady_clock;
    using Profile = std::array<Microamps, kPhaseCount>;

    explicit EnergyLedger(Profile profile) noexcept : profile_{profile} {}

    // Дописує вже виміряний відрізок фази (розрахунковий режим).
    void account(Phase phase, std::chrono::microseconds duration) noexcept;

    // Перемикання фаз у реальному часі: закриває попередню, відкриває нову.
    void enter(Phase phase) noexcept;
    void stop() noexcept;

    [[nodiscard]] Microamps average_current() const noexcept;
    [[nodiscard]] double    charge_uah() const noexcept;
    [[nodiscard]] double    charge_share(Phase phase) const noexcept;
    [[nodiscard]] double    time_share(Phase phase) const noexcept;

    // Прогноз ресурсу джерела живлення за накопиченим середнім струмом.
    [[nodiscard]] std::chrono::hours predicted_life(double battery_mah) const noexcept;

    [[nodiscard]] Budget audit(double battery_mah,
                               std::chrono::hours required) const noexcept;

    [[nodiscard]] static std::string_view name(Phase phase) noexcept;

private:
    [[nodiscard]] static constexpr std::size_t index(Phase phase) noexcept
    {
        return static_cast<std::size_t>(phase);
    }

    Profile                                           profile_{};
    std::array<std::chrono::microseconds, kPhaseCount> time_{};
    std::array<std::uint64_t, kPhaseCount>             charge_{}; // мкА·мкс
    std::chrono::microseconds                          total_time_{0};
    std::uint64_t                                      total_charge_{0};

    Phase             active_{Phase::Sleep};
    Clock::time_point started_{};
    bool              running_{false};
};

} // namespace budget
