// BenchRun.hpp — кінцевий автомат стендового прогону Compass-Mot.
//
// Залізо заходить крізь інтерфейс Rig, тож той самий автомат крутиться
// і на платі, і на моделі стенда в main.cpp.
#pragma once

#include "CompassMot.hpp"

#include <chrono>
#include <expected>
#include <optional>
#include <string_view>

namespace compassmot {

enum class Phase {
    Idle,
    Baseline,    // 2 с при зупинених моторах: знімаємо B_base
    RampUp,      // сходинки газу по 10%
    PeakHold,    // 1.5 с на 85%
    RampDown,    // плавний скид: бережемо ключі від зворотної ЕРС
    Solve,
    Save,
    Done,
    Failed
};

[[nodiscard]] std::string_view name(Phase phase) noexcept;

// Контракт із залізом стенда.
class Rig {
public:
    virtual ~Rig() = default;

    virtual Vector3 read_field() = 0;              // мкТл
    virtual float   read_current() = 0;            // А з шунта Power Module
    virtual void    set_throttle(float pct) = 0;   // 0..100
    virtual bool    store(const Vector3& k) = 0;   // EEPROM/FRAM
};

class BenchRun {
public:
    using millis = std::chrono::milliseconds;

    explicit BenchRun(Rig& rig) noexcept : rig_{&rig} {}

    // Один такт автомата з періодом польотного циклу (10 мс).
    Phase step(millis now);

    // Аварійна зупинка ззовні: кнопка, зникнення зв'язку, зірваний гвинт.
    void abort(std::string_view reason) noexcept;

    [[nodiscard]] Phase phase() const noexcept { return phase_; }
    [[nodiscard]] float throttle() const noexcept { return throttle_pct_; }
    [[nodiscard]] std::size_t collected() const noexcept;
    [[nodiscard]] std::string_view failure() const noexcept { return failure_; }

    // Дійсний у Done і Failed.
    [[nodiscard]] const std::expected<Fit, FitError>& outcome() const noexcept {
        return outcome_;
    }

private:
    void enter(Phase phase, millis now) noexcept;
    void set_throttle(float pct) noexcept;
    void fail(std::string_view reason, FitError err, millis now) noexcept;
    // Спільна для «газованих» станів охорона; false — прогін щойно впав.
    bool guard_and_sample(millis now, bool collect);

    Rig*   rig_;
    Phase  phase_{Phase::Idle};
    millis t_phase_{0};
    millis t_step_{0};
    float  throttle_pct_{0.0f};

    Vector3     base_sum_{};
    std::size_t base_n_{0};

    std::optional<OlsAccumulator> ols_;
    std::expected<Fit, FitError>  outcome_{std::unexpected(FitError::TooFewSamples)};
    std::string_view              failure_{};
};

}  // namespace compassmot
