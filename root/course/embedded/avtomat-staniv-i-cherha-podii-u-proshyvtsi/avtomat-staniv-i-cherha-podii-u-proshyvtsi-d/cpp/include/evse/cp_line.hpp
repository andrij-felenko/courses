#pragma once

#include <cstdint>
#include <optional>
#include <string_view>

#include "evse/units.hpp"

namespace evse {

/*
 * Клас лінії Control Pilot за IEC 61851-1 / SAE J1772. Класифікація —
 * чиста constexpr-функція без стану, тож її можна прогнати на сталих просто
 * під час компіляції, що нижче й робить static_assert.
 */
enum class CpClass : std::uint8_t {
    A,      /* +12 В, кабель не підключено */
    B,      /* +9 В, штекер у гнізді */
    C,      /* +6 В, автомобіль просить струм */
    Invalid /* обрив, коротке, зниклий діод, збита частота */
};

[[nodiscard]] constexpr std::string_view name(CpClass c) noexcept
{
    switch (c) {
        case CpClass::A: return "A (+12 В, кабель від'єднано)";
        case CpClass::B: return "B (+9 В, підключено)";
        case CpClass::C: return "C (+6 В, запит енергії)";
        default:         return "аварія лінії пілота";
    }
}

/*
 * Смуги напруги додатного півперіоду розділені мертвими зонами: вимір, що
 * потрапив у зазор, не належить жодному класу. Так деренчання на межі не
 * породжує зливи подій.
 */
struct CpBands {
    static constexpr Millivolts kAMin{10800};
    static constexpr Millivolts kAMax{13000};
    static constexpr Millivolts kBMin{7700};
    static constexpr Millivolts kBMax{10200};
    static constexpr Millivolts kCMin{4800};
    static constexpr Millivolts kCMax{7300};

    /* Від'ємний півперіод мусить сягати приблизно −12 В: його зникнення
     * означає пробитий або відсутній діод в автомобілі. */
    static constexpr Millivolts kNegativeMax{-10000};

    static constexpr Micros kPeriodMin{950};
    static constexpr Micros kPeriodMax{1050};
};

/*
 * std::nullopt означає «вимір у мертвій зоні»: він не підтверджує клас, але й
 * не спростовує попередній.
 */
[[nodiscard]] constexpr std::optional<CpClass> classify(Millivolts high, Millivolts low,
                                                        Micros period, bool pwmActive) noexcept
{
    if (pwmActive && (period < CpBands::kPeriodMin || period > CpBands::kPeriodMax)) {
        return CpClass::Invalid;
    }

    if (high >= CpBands::kAMin && high <= CpBands::kAMax) {
        return CpClass::A; /* автомобіля немає, від'ємного півперіоду може не бути */
    }

    /* Нижче класу A лінію навантажує автомобіль — тоді діод обов'язковий. */
    if (low > CpBands::kNegativeMax) {
        return CpClass::Invalid;
    }

    if (high >= CpBands::kBMin && high <= CpBands::kBMax) {
        return CpClass::B;
    }
    if (high >= CpBands::kCMin && high <= CpBands::kCMax) {
        return CpClass::C;
    }

    /* Нижче 4,8 В — стан D (вентиляція) або аварія: станція обидва випадки
     * трактує однаково. Вище 13 В — пробій із силової мережі. */
    if (high < CpBands::kCMin || high > CpBands::kAMax) {
        return CpClass::Invalid;
    }

    return std::nullopt; /* мертва зона між смугами */
}

static_assert(classify(12000_mV, Millivolts{-12000}, Micros{0}, false) == CpClass::A);
static_assert(classify(9000_mV, Millivolts{-12000}, Micros{1000}, true) == CpClass::B);
static_assert(classify(6000_mV, Millivolts{-12000}, Micros{1000}, true) == CpClass::C);
static_assert(classify(6000_mV, 0_mV, Micros{1000}, true) == CpClass::Invalid);
static_assert(classify(9000_mV, Millivolts{-12000}, Micros{1400}, true) == CpClass::Invalid);
static_assert(!classify(10500_mV, Millivolts{-12000}, Micros{1000}, true).has_value());

/*
 * Підтвердження класу серією однакових вимірів. Повертає новий клас лише в
 * ту мить, коли він справді змінився, — усі інші виміри мовчать, і черга
 * подій лишається порожньою, доки на лінії нічого не відбувається.
 */
class CpDebouncer {
public:
    static constexpr std::uint8_t kSamples = 3; /* 3 × 10 мс = 30 мс */

    [[nodiscard]] std::optional<CpClass> update(std::optional<CpClass> raw) noexcept
    {
        if (!raw) {
            return std::nullopt;
        }

        if (*raw != candidate_) {
            candidate_ = *raw;
            streak_    = 1;
            return std::nullopt;
        }

        if (streak_ < kSamples) {
            ++streak_;
        }
        if (streak_ < kSamples || (stable_ && *stable_ == *raw)) {
            return std::nullopt;
        }

        stable_ = *raw;
        return stable_;
    }

    [[nodiscard]] std::optional<CpClass> stable() const noexcept { return stable_; }

private:
    std::optional<CpClass> stable_{};
    CpClass                candidate_{CpClass::A};
    std::uint8_t           streak_{0};
};

} // namespace evse
