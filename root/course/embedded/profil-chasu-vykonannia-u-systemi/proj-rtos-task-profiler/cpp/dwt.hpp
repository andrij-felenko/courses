// dwt.hpp — блок DWT ядра Cortex-M: лічильник тактів і лічильники подій.
//
// Шар голого заліза, header-only: доступ до регістрів PPB, увімкнення CYCCNT
// і програмне розширення 8-розрядних лічильників подій до 32 розрядів.
#pragma once

#include <cstdint>

namespace dwt {

namespace detail {

inline constexpr std::uintptr_t kDemcr = 0xE000EDFCU;
inline constexpr std::uintptr_t kCtrl = 0xE0001000U;
inline constexpr std::uintptr_t kCyccnt = 0xE0001004U;
inline constexpr std::uintptr_t kCpicnt = 0xE0001008U;
inline constexpr std::uintptr_t kExccnt = 0xE000100CU;
inline constexpr std::uintptr_t kSleepcnt = 0xE0001010U;
inline constexpr std::uintptr_t kLsucnt = 0xE0001014U;
inline constexpr std::uintptr_t kFoldcnt = 0xE0001018U;
inline constexpr std::uintptr_t kLar = 0xE0001FB0U; // CoreSight Lock Access

[[nodiscard]] inline volatile std::uint32_t& reg(std::uintptr_t address) noexcept
{
    return *reinterpret_cast<volatile std::uint32_t*>(address);
}

} // namespace detail

inline constexpr std::uint32_t kTrcena = 1U << 24;      // живлення логіки трасування
inline constexpr std::uint32_t kLarKey = 0xC5ACCE55U;   // ключ зняття замка
inline constexpr std::uint32_t kCyccntEna = 1U << 0;
inline constexpr std::uint32_t kCpiEvtEna = 1U << 17;
inline constexpr std::uint32_t kExcEvtEna = 1U << 18;
inline constexpr std::uint32_t kSleepEvtEna = 1U << 19;
inline constexpr std::uint32_t kLsuEvtEna = 1U << 20;
inline constexpr std::uint32_t kFoldEvtEna = 1U << 21;
inline constexpr std::uint32_t kNoPrfCnt = 1U << 24;    // лічильників подій немає
inline constexpr std::uint32_t kNoCycCnt = 1U << 25;    // CYCCNT не реалізовано

// Найдешевше читання: одна інструкція LDR по приватній периферійній шині.
[[nodiscard]] inline std::uint32_t cyccnt() noexcept
{
    return detail::reg(detail::kCyccnt);
}

// Читання з бар'єрами — коли мітка не сміє переїхати через досліджуваний код.
[[nodiscard]] inline std::uint32_t cyccnt_serialized() noexcept
{
    __asm__ volatile("" ::: "memory");
    __asm__ volatile("dsb 0xF" ::: "memory");
    __asm__ volatile("isb 0xF" ::: "memory");
    const std::uint32_t value = detail::reg(detail::kCyccnt);
    __asm__ volatile("" ::: "memory");
    return value;
}

[[nodiscard]] inline bool has_cycle_counter() noexcept
{
    return (detail::reg(detail::kCtrl) & kNoCycCnt) == 0U;
}

[[nodiscard]] inline bool has_event_counters() noexcept
{
    return (detail::reg(detail::kCtrl) & kNoPrfCnt) == 0U;
}

// Вмикає CYCCNT і переконується, що він справді лічить: без під'єднаного
// відладчика домен трасування на частині ядер лишається без живлення, і
// регістр читається сталим нулем. Мовчазний нуль гірший за чесне false.
[[nodiscard]] inline bool enable_cycle_counter() noexcept
{
    detail::reg(detail::kDemcr) |= kTrcena;
    detail::reg(detail::kLar) = kLarKey; // на ядрах без замка запис нешкідливий

    if (!has_cycle_counter()) {
        return false;
    }

    detail::reg(detail::kCyccnt) = 0U;
    detail::reg(detail::kCtrl) |= kCyccntEna;

    const std::uint32_t before = cyccnt();
    for (volatile int i = 0; i < 8; ++i) {
        // коротка затримка, щоб лічильник устиг зрушити
    }
    return cyccnt() != before;
}

// Лічильники подій рахують лише коли ввімкнено відповідний біт EVTENA.
inline void enable_event_counters() noexcept
{
    if (!has_event_counters()) {
        return;
    }
    detail::reg(detail::kCpicnt) = 0U;
    detail::reg(detail::kExccnt) = 0U;
    detail::reg(detail::kSleepcnt) = 0U;
    detail::reg(detail::kLsucnt) = 0U;
    detail::reg(detail::kFoldcnt) = 0U;
    detail::reg(detail::kCtrl) |=
        kCpiEvtEna | kExcEvtEna | kSleepEvtEna | kLsuEvtEna | kFoldEvtEna;
}

// Лічильники подій — 8-розрядні: крутяться через нуль кожні 256 підрахованих
// тактів. Клас тримає копію останнього байта й доліковує беззнакову різницю в
// 32-розрядні накопичувачі. Розширення точне, поки між викликами sample()
// назбирується менш ніж 256 подій: на кожному перемиканні контексту цього
// вистачає для EXCCNT і LSUCNT, але не для довгого tickless-сну — там
// рахують пакети переповнення ITM або власний облік RTOS.
class EventCounters {
public:
    struct Totals {
        std::uint32_t cpi{};   // такти простою конвеєра
        std::uint32_t exc{};   // стекінг, анстекінг і код обробників переривань
        std::uint32_t sleep{}; // такти в WFI/WFE
        std::uint32_t lsu{};   // очікування блоку завантаження/збереження
        std::uint32_t fold{};  // «згорнуті» переходи
    };

    void reset() noexcept
    {
        totals_ = Totals{};
        last_ = read_bytes();
    }

    void sample() noexcept
    {
        const Bytes now = read_bytes();
        // різниця в 8 розрядах коректна й через переповнення — той самий
        // додатковий код, що й для 32-розрядного CYCCNT
        totals_.cpi += static_cast<std::uint8_t>(now.cpi - last_.cpi);
        totals_.exc += static_cast<std::uint8_t>(now.exc - last_.exc);
        totals_.sleep += static_cast<std::uint8_t>(now.sleep - last_.sleep);
        totals_.lsu += static_cast<std::uint8_t>(now.lsu - last_.lsu);
        totals_.fold += static_cast<std::uint8_t>(now.fold - last_.fold);
        last_ = now;
    }

    [[nodiscard]] const Totals& totals() const noexcept { return totals_; }

private:
    struct Bytes {
        std::uint8_t cpi{}, exc{}, sleep{}, lsu{}, fold{};
    };

    [[nodiscard]] static Bytes read_bytes() noexcept
    {
        return Bytes{static_cast<std::uint8_t>(detail::reg(detail::kCpicnt)),
                     static_cast<std::uint8_t>(detail::reg(detail::kExccnt)),
                     static_cast<std::uint8_t>(detail::reg(detail::kSleepcnt)),
                     static_cast<std::uint8_t>(detail::reg(detail::kLsucnt)),
                     static_cast<std::uint8_t>(detail::reg(detail::kFoldcnt))};
    }

    Totals totals_{};
    Bytes last_{};
};

} // namespace dwt
