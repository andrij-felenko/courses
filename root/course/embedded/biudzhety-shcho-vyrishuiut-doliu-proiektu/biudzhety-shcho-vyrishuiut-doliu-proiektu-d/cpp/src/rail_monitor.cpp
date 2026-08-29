#include "budget/rail_monitor.hpp"

#include <algorithm>

namespace budget {

Budget RailMonitor::sample(double volts) noexcept
{
    last_v_ = volts;
    min_v_  = std::min(min_v_, volts);
    ++samples_;

    if (volts <= limits_.bor_v) {
        ++brownouts_;
        ++sags_;
        return Budget::RailBrownout | Budget::RailSag;
    }
    if (volts < limits_.warn_v) {
        ++sags_;
        return Budget::RailSag;
    }
    return Budget::None;
}

} // namespace budget
