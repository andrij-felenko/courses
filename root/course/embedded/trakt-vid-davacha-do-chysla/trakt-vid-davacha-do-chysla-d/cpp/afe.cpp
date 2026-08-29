#include "afe.hpp"

#include <algorithm>
#include <cmath>
#include <numbers>

namespace {

// Похибки цього конкретного примірника — те, заради чого й існує калібрування.
constexpr double kGainTolerance   = 1.008;   // 0.8 % розкиду R_g і внутрішніх резисторів
constexpr double kBridgeOffsetV   = 0.00012; // несиметрія моста, диференційно
constexpr double kLevelShiftReal  = 1.6478;  // дільник середньої точки теж не ідеальний

// Завади (розділи 2 і 3).
constexpr double kMainsHz         = 50.0;
constexpr double kMainsResidualV  = 40.0e-6; // залишок наводки ПІСЛЯ придушення синфазної
constexpr double kPwmHz           = 980.0;   // комутація драйвера двигуна поруч на платі
constexpr double kPwmOutputV      = 0.012;   // наводиться вже на вихідну доріжку
constexpr double kThermalNoiseV   = 0.0004;  // СКВ шуму тракту, приведене до виходу

constexpr double kAafCornerHz     = 500.0;   // зріз RC-ланки перед входом АЦП
constexpr double kActualGain      = kInAmpGain * kGainTolerance;

[[nodiscard]] double sineAt(double amplitude, double hertz, double seconds) noexcept
{
    return amplitude * std::sin(2.0 * std::numbers::pi * hertz * seconds);
}

[[nodiscard]] std::uint16_t quantize(double volts) noexcept
{
    if (volts <= 0.0) {
        return 0; // за шкалою знизу: більше АЦП сказати нічого не може
    }
    const double code = std::floor(volts / kAdcReference * kAdcLevels);
    return static_cast<std::uint16_t>(std::min(code, static_cast<double>(kAdcMaxCode)));
}

} // namespace

AnalogFrontEnd::AnalogFrontEnd(std::uint64_t seed, AntiAliasFilter filter)
    : filter_{filter}
    , rng_{seed}
    , thermalNoise_{0.0, kThermalNoiseV}
{
    // Фільтр стартує з усталеного значення: інакше перші мілісекунди моделі
    // показували б заряд конденсатора, а не поведінку тракту.
    filterState_ = kActualGain * kBridgeOffsetV + kLevelShiftReal;
}

double AnalogFrontEnd::outputVoltage()
{
    // Диференційний бік: корисний сигнал, несиметрія моста і залишок мережевої
    // наводки. Синфазних 2.5 В тут немає взагалі — In-Amp прибрав їх на 110 дБ.
    const double differential = kBridgeSensitivity * load_
                              + kBridgeOffsetV
                              + sineAt(kMainsResidualV, kMainsHz, time_);

    double output = kActualGain * differential + kLevelShiftReal;

    // ШІМ наводиться на вихідну доріжку — підсилювач її вже не бачить,
    // а ключ вибірки АЦП побачить.
    output += sineAt(kPwmOutputV, kPwmHz, time_);
    output += thermalNoise_(rng_);

    return output;
}

std::uint16_t AnalogFrontEnd::step()
{
    const double output = outputVoltage();
    time_ += kAnalogStepSeconds;

    if (filter_ == AntiAliasFilter::Absent) {
        return quantize(output); // на ключ іде все, включно з 980 Гц
    }

    // Однополюсна RC-ланка в дискретній формі: alpha = dt / (RC + dt).
    const double rc = 1.0 / (2.0 * std::numbers::pi * kAafCornerHz);
    const double alpha = kAnalogStepSeconds / (rc + kAnalogStepSeconds);

    filterState_ += (output - filterState_) * alpha;
    return quantize(filterState_);
}
