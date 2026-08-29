// bsp/power_rail.cpp
#include "bsp/power_rail.hpp"

namespace bsp {

bool PowerRail::on() { return enable_.write(active_level_).has_value(); }

bool PowerRail::off() { return enable_.write(hal::invert(active_level_)).has_value(); }

bool PowerRail::power_cycle()
{
    if (!off()) {
        return false;
    }
    // Без витримки ємності на платі не встигають розрядитись, і давач
    // «переживає» скидання, лишаючись у тому самому завислому стані.
    clock_.sleep_for(off_hold_);

    if (!on()) {
        return false;
    }
    clock_.sleep_for(startup_);

    ++cycles_;
    return true;
}

}  // namespace bsp
