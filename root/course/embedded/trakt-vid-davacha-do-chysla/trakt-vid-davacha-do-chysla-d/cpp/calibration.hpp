#pragma once

// Двоточкове лінійне калібрування (розділ 5). Компенсує ОДРАЗУ всі статичні
// похибки тракту: несиметрію моста, зсув нуля підсилювачів, розкид R_g,
// неточність V_ref і чутливості давача. Номіналів на платі для цього знати не
// треба — треба дві еталонні точки.

#include <cstdint>
#include <expected>
#include <string_view>

enum class CalibrationError {
    SpanTooSmall,  // точки не розійшлися: обрив, насичення або забута гиря
    SameWeight,    // дві точки з однаковою вагою нахилу не задають
};

[[nodiscard]] constexpr std::string_view describe(CalibrationError error) noexcept
{
    switch (error) {
    case CalibrationError::SpanTooSmall: return "коди калібрувальних точок майже збіглися";
    case CalibrationError::SameWeight:   return "обидві точки мають однакову вагу";
    }
    return "невідома похибка калібрування";
}

class TwoPointCalibration {
public:
    // Менша різниця кодів означала б ділення на майже нуль: шкалу, де один квант
    // шуму важить кілограми. Прошивка мусить відмовитися й лишити стару таблицю,
    // а не мовчки прийняти зіпсоване калібрування.
    static constexpr std::int32_t kMinimumSpanCounts = 100;

    [[nodiscard]] static std::expected<TwoPointCalibration, CalibrationError>
    create(std::int32_t zeroCode, double zeroKilograms,
           std::int32_t spanCode, double spanKilograms) noexcept
    {
        const std::int32_t span = spanCode - zeroCode;
        if (span > -kMinimumSpanCounts && span < kMinimumSpanCounts) {
            return std::unexpected(CalibrationError::SpanTooSmall);
        }
        if (zeroKilograms == spanKilograms) {
            return std::unexpected(CalibrationError::SameWeight);
        }
        return TwoPointCalibration{zeroCode, zeroKilograms, spanCode, spanKilograms};
    }

    // X = (N - N1) * (X2 - X1) / (N2 - N1) + X1. Тут, на відміну від
    // мікроконтролерного варіанта, плаваюча кома є — тож і фізика в кілограмах.
    [[nodiscard]] double toKilograms(std::int32_t code) const noexcept
    {
        const double codeSpan = static_cast<double>(spanCode_) - zeroCode_;
        return zeroKilograms_
             + (static_cast<double>(code) - zeroCode_) * (spanKilograms_ - zeroKilograms_)
                   / codeSpan;
    }

    // Скільки квантів АЦП припадає на кілограм за цим калібруванням: саме це
    // число порівнюють із розрахунковим, щоб побачити похибку чутливості.
    [[nodiscard]] double countsPerKilogram() const noexcept
    {
        return (static_cast<double>(spanCode_) - zeroCode_)
             / (spanKilograms_ - zeroKilograms_);
    }

private:
    constexpr TwoPointCalibration(std::int32_t zeroCode, double zeroKilograms,
                                  std::int32_t spanCode, double spanKilograms) noexcept
        : zeroCode_{zeroCode}
        , spanCode_{spanCode}
        , zeroKilograms_{zeroKilograms}
        , spanKilograms_{spanKilograms}
    {
    }

    std::int32_t zeroCode_;
    std::int32_t spanCode_;
    double       zeroKilograms_;
    double       spanKilograms_;
};
