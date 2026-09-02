#include "day_match.hpp"

namespace minicron {

// Зірочка не обмежує нічого: диз'юнкція з нею завжди давала б істину, і
// розклад «0 3 15 * *» спрацьовував би щодня. Тому:
//
//   DOM або DOW записані зірочкою  →  кон'юнкція  (обидва обмеження разом)
//   обидва поля задані явно        →  диз'юнкція  (досить одного збігу)
//
// Пастка «31 лютого» сюди не потрапляє: у лютому просто не буває дня з
// tm_mday == 31, тож біт 31 ніколи не перевіряється.
bool DayFields::matches(const std::tm& now) const noexcept
{
    const int mday = now.tm_mday;
    const int wday = now.tm_wday;
    if (mday < 1 || mday > 31 || wday < 0 || wday > 6) {
        return false;
    }

    const bool dom_hit = dom.test(static_cast<std::size_t>(mday));
    const bool dow_hit = dow.test(static_cast<std::size_t>(wday));

    if (dom_star || dow_star) {
        return dom_hit && dow_hit;
    }
    return dom_hit || dow_hit;
}

std::string_view DayFields::rule() const noexcept
{
    return (dom_star || dow_star) ? "кон'юнкція (DOM І DOW)"
                                  : "диз'юнкція (DOM АБО DOW)";
}

}  // namespace minicron
