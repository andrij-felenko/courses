#pragma once

// Словник порушень бюджетів.
//
// Порушення — це набір, а не одне значення: просідання шини й переповнення
// стеку трапляються одночасно й вимагають різних дій. Тому enum class із
// набором операцій, а не послідовність окремих кодів помилок.

#include <cstdint>
#include <string>
#include <string_view>

namespace budget {

enum class Budget : std::uint32_t {
    None = 0,

    // Пам'ять
    StackLow        = 1u << 0,  // запас стеку впав нижче резерву
    StackOverflow   = 1u << 1,  // сторожове слово стеку затерте
    HeapLow         = 1u << 2,  // сумарний вільний обсяг кучі малий
    HeapFragmented  = 1u << 3,  // вільного багато, суцільного блоку немає
    FlashNoOta      = 1u << 4,  // образ не влазить у пасивний слот
    FlashTight      = 1u << 5,  // образ перетнув 45 % повного Flash

    // Живлення та енергія
    RailSag         = 1u << 6,
    RailBrownout    = 1u << 7,
    EnergyOver      = 1u << 8,

    // Тепло
    ThermalWarning  = 1u << 9,
    ThermalTrip     = 1u << 10,

    // Час
    DeadlineMiss    = 1u << 11
};

[[nodiscard]] constexpr Budget operator|(Budget lhs, Budget rhs) noexcept
{
    return static_cast<Budget>(static_cast<std::uint32_t>(lhs) |
                               static_cast<std::uint32_t>(rhs));
}

[[nodiscard]] constexpr Budget operator&(Budget lhs, Budget rhs) noexcept
{
    return static_cast<Budget>(static_cast<std::uint32_t>(lhs) &
                               static_cast<std::uint32_t>(rhs));
}

constexpr Budget& operator|=(Budget& lhs, Budget rhs) noexcept
{
    lhs = lhs | rhs;
    return lhs;
}

[[nodiscard]] constexpr bool any(Budget flags) noexcept
{
    return static_cast<std::uint32_t>(flags) != 0u;
}

[[nodiscard]] constexpr bool contains(Budget flags, Budget probe) noexcept
{
    return any(flags & probe);
}

// Порушення, після яких пристрій не має права продовжувати штатну роботу.
inline constexpr Budget kCritical = Budget::StackOverflow |
                                    Budget::RailBrownout |
                                    Budget::ThermalTrip |
                                    Budget::HeapFragmented;

enum class Severity { Ok, Warning, Critical };

[[nodiscard]] constexpr Severity severity(Budget flags) noexcept
{
    if (contains(flags, kCritical)) {
        return Severity::Critical;
    }
    return any(flags) ? Severity::Warning : Severity::Ok;
}

enum class Action { Run, Derate, SafeState };

[[nodiscard]] constexpr Action action(Budget flags) noexcept
{
    switch (severity(flags)) {
    case Severity::Critical: return Action::SafeState;
    case Severity::Warning:  return Action::Derate;
    default:                 return Action::Run;
    }
}

[[nodiscard]] std::string describe(Budget flags);
[[nodiscard]] std::string_view describe(Action action) noexcept;

} // namespace budget
