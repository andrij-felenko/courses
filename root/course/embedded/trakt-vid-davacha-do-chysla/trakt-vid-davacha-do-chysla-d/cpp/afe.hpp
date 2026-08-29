#pragma once

// Модель аналогового тракту з розділів 2-4: тензоміст -> інструментальний
// підсилювач AD620 -> зміщення рівня -> антиаліасинговий RC-фільтр -> 12-бітний
// АЦП. Аналогова напруга рахується з кроком 10 мкс — на цій же сітці працює
// передискретизація з розділу 3.
//
// У заголовку живуть ПАСПОРТНІ величини: за ними прошивка робить свій
// розрахунковий перерахунок. Похибки конкретного примірника заховані в afe.cpp
// саме тому, що прошивка їх не знає й знати не може.

#include <cstdint>
#include <random>

inline constexpr double kAnalogStepSeconds = 1.0e-5;
inline constexpr int    kAnalogStepHz      = 100'000;

inline constexpr double kAdcReference = 3.3;   // В
inline constexpr int    kAdcLevels    = 4096;  // 2^12
inline constexpr int    kAdcMaxCode   = kAdcLevels - 1;

inline constexpr double kInAmpR1           = 24'700.0; // внутрішні резистори AD620
inline constexpr double kInAmpRg           = 330.0;    // зовнішній резистор підсилення
inline constexpr double kInAmpGain         = 1.0 + 2.0 * kInAmpR1 / kInAmpRg; // ≈ 150.7
inline constexpr double kBridgeSensitivity = 0.0005;   // 2 мВ/В при 5 В і межі 20 кг
inline constexpr double kLevelShiftNominal = kAdcReference / 2.0;

// Скільки квантів АЦП мав би давати кілограм за паспортом.
[[nodiscard]] inline constexpr double nominalCountsPerKilogram() noexcept
{
    return kInAmpGain * kBridgeSensitivity * kAdcLevels / kAdcReference;
}

// Код порожньої платформи в ідеальному тракті.
inline constexpr std::int32_t kNominalZeroCode =
    static_cast<std::int32_t>(kLevelShiftNominal / kAdcReference * kAdcLevels);

enum class AntiAliasFilter { Absent, Present };

class AnalogFrontEnd {
public:
    AnalogFrontEnd(std::uint64_t seed, AntiAliasFilter filter);

    void setLoad(double kilograms) noexcept { load_ = kilograms; }

    // Просуває аналоговий час на kAnalogStepSeconds і повертає код АЦП у цю мить.
    // Стробувати рідше можна — але тоді все, що діялося між стробами, зникає
    // назавжди, і жоден цифровий фільтр цього вже не поверне.
    [[nodiscard]] std::uint16_t step();

private:
    [[nodiscard]] double outputVoltage();

    double          time_{0.0};
    double          filterState_{0.0};
    double          load_{0.0};
    AntiAliasFilter filter_;
    std::mt19937_64 rng_;
    // Тепловий шум Джонсона гаусів за природою, тож і в моделі він гаусів.
    std::normal_distribution<double> thermalNoise_;
};
