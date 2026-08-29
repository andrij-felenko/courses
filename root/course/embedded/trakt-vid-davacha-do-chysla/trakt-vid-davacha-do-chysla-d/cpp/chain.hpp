#pragma once

// Тракт прошивки в зборі: АЦП -> проріджування -> рухоме середнє на період
// мережі -> експоненційне згладжування. Калібрування свідомо лишається поза
// цим класом: воно міняється від примірника до примірника й живе в
// енергонезалежній пам'яті, а фільтри однакові для всіх плат.

#include "afe.hpp"
#include "filters.hpp"

#include <cstddef>
#include <cstdint>
#include <optional>

inline constexpr int kChainRateHz = 1000; // частота відліків, з якою працює прошивка
inline constexpr int kMainsHz     = 50;

inline constexpr std::size_t kDecimationFactor = kAnalogStepHz / kChainRateHz; // 100
inline constexpr std::size_t kNotchWindow      = kChainRateHz / kMainsHz;      // 20 відліків = період 50 Гц
inline constexpr unsigned    kSmootherShift    = 5;                            // alpha = 1/32, ~32 мс

enum class Sampling {
    Direct,      // один строб на мілісекунду — і все, що між стробами, втрачено
    Oversampled, // 100 кГц з накопиченням і скиданням до 1 кГц
};

class MeasurementChain {
public:
    struct Taps {
        std::int32_t raw;           // те, що прийшло з АЦП (у режимі проріджування — Q4)
        std::int32_t afterNotch;    // після рухомого середнього
        std::int32_t afterSmoother; // після згладжування: це число йде в калібрування
    };

    explicit MeasurementChain(Sampling mode) noexcept : mode_{mode} {}

    // Просуває тракт рівно на одну мілісекунду. Аналогова модель живе всі сто
    // кроків по 10 мкс незалежно від того, коли АЦП вирішив стробувати, — саме
    // ця нерівність і породжує аліасинг у режимі Direct.
    //
    // Порожній результат означає «вікно рухомого середнього ще не заповнене»:
    // такий відлік не можна ні показувати, ні брати в калібрування.
    [[nodiscard]] std::optional<Taps> advanceOneMillisecond(AnalogFrontEnd& afe);

    // У скільки разів коди цього тракту дрібніші за квант АЦП.
    [[nodiscard]] std::int32_t rawScale() const noexcept
    {
        return mode_ == Sampling::Oversampled ? Decimator<kDecimationFactor>::scale() : 1;
    }

private:
    Sampling                            mode_;
    Decimator<kDecimationFactor>        decimator_{};
    MovingAverage<kNotchWindow>         notch_{};
    ExponentialSmoother<kSmootherShift> smoother_{};
};
