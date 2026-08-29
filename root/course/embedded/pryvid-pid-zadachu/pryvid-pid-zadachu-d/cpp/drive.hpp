#pragma once

#include <numbers>
#include <optional>
#include <string_view>

namespace drive {

enum class Family { Brushed, Stepper, Brushless, Servo };

[[nodiscard]] std::string_view familyName(Family family) noexcept;

[[nodiscard]] constexpr double rpmToRadS(double rpm) noexcept {
    return rpm * (2.0 * std::numbers::pi / 60.0);
}

[[nodiscard]] constexpr double radSToRpm(double omegaRadS) noexcept {
    return omegaRadS * (60.0 / (2.0 * std::numbers::pi));
}

// Режим, у якому рахують мідні втрати: кроковий у спокої бере скорочений струм.
enum class Regime { Moving, Standstill };

// Паспорт мотора. Уся фізика — методи: рахується вона тільки з цих чисел
// і ніде більше не потрібна.
struct Motor {
    std::string_view name{};
    Family family{Family::Brushed};
    double ratedTorqueNm{};            // тривалий момент; у крокового — момент утримання
    double noLoadSpeedRpm{};           // холостий хід або паспортна межа обертів
    double cornerSpeedRpm{};           // кроковий: злам кривої; BLDC: базова швидкість
    double ratedCurrentA{};
    double phaseResistanceOhm{};
    double rotorInertiaKgm2{};
    double thermalResistanceCPerW{};
    double supplyV{};
    double holdCurrentFraction{1.0};   // кроковий у спокої: частка номіналу
    double stepResolutionDeg{};        // 0 — давача положення немає

    [[nodiscard]] double torqueConstant() const noexcept;              // k_t = T / I
    [[nodiscard]] double stallCurrentA() const noexcept;
    [[nodiscard]] double availableTorqueNm(double omegaRadS) const noexcept;
    [[nodiscard]] double currentForTorqueA(double torqueNm) const noexcept;
    [[nodiscard]] double copperLossW(double torqueNm, Regime regime) const noexcept;
    [[nodiscard]] double windingTempC(double averageLossW, double ambientC) const noexcept;

    // Порожньо — паспорт несуперечливий.
    [[nodiscard]] std::optional<std::string_view> problem() const noexcept;
};

struct Gearbox {
    double ratio{1.0};         // N = w_motor / w_load
    double efficiency{1.0};
    double backlashDeg{0.0};

    [[nodiscard]] double reflectTorque(double loadTorqueNm) const noexcept;
    [[nodiscard]] double reflectInertia(double loadInertiaKgm2) const noexcept;
    [[nodiscard]] double heatLossW(double outputPowerW) const noexcept;
    [[nodiscard]] std::optional<std::string_view> problem() const noexcept;
};

// Кандидат на полиці — це завжди пара «мотор + передача».
struct Unit {
    Motor motor{};
    Gearbox gear{};
};

}  // namespace drive
