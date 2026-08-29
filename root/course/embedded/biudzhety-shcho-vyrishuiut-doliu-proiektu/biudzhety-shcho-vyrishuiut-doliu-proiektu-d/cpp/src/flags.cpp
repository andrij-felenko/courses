#include "budget/flags.hpp"

#include <array>
#include <utility>

namespace budget {
namespace {

using Entry = std::pair<Budget, std::string_view>;

constexpr std::array<Entry, 12> kNames{{
    { Budget::StackLow,       "СТЕК:ЗАПАС" },
    { Budget::StackOverflow,  "СТЕК:ПЕРЕПОВНЕННЯ" },
    { Budget::HeapLow,        "КУЧА:ЗАПАС" },
    { Budget::HeapFragmented, "КУЧА:ФРАГМЕНТАЦІЯ" },
    { Budget::FlashNoOta,     "FLASH:БЕЗ-OTA" },
    { Budget::FlashTight,     "FLASH:ТІСНО" },
    { Budget::RailSag,        "ШИНА:ПРОСІДАННЯ" },
    { Budget::RailBrownout,   "ШИНА:BOR" },
    { Budget::EnergyOver,     "ЕНЕРГІЯ:ПЕРЕВИТРАТА" },
    { Budget::ThermalWarning, "ТЕПЛО:ЗАПАС" },
    { Budget::ThermalTrip,    "ТЕПЛО:T_j_max" },
    { Budget::DeadlineMiss,   "ЧАС:ЗРИВ-ТЕРМІНУ" }
}};

} // namespace

std::string describe(Budget flags)
{
    if (!any(flags)) {
        return "усі бюджети в межах";
    }

    std::string text;
    for (const auto& [flag, name] : kNames) {
        if (!contains(flags, flag)) {
            continue;
        }
        if (!text.empty()) {
            text += ", ";
        }
        text += name;
    }
    return text;
}

std::string_view describe(Action action) noexcept
{
    switch (action) {
    case Action::Run:       return "штатна робота";
    case Action::Derate:    return "знизити темп";
    case Action::SafeState: return "безпечний стан";
    }
    return "?";
}

} // namespace budget
