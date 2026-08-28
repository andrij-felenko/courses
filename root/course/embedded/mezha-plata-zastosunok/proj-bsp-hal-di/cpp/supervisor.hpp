// --- supervisor.hpp: Бізнес-логіка (100% переносний код) ---
#ifndef SUPERVISOR_HPP
#define SUPERVISOR_HPP

#include "bsp_interface.hpp"

namespace app {

class SystemSupervisor {
public:
    explicit SystemSupervisor(bsp::IBoardSupport& bsp) noexcept
        : bsp_(bsp), is_low_power_warning_(false), is_critical_shutdown_(false) {}

    void run_cycle() noexcept;

    [[nodiscard]] bool is_low_power_warning() const noexcept { return is_low_power_warning_; }
    [[nodiscard]] bool is_critical_shutdown() const noexcept { return is_critical_shutdown_; }

private:
    bsp::IBoardSupport& bsp_;
    bool is_low_power_warning_;
    bool is_critical_shutdown_;
};

} // namespace app

#endif /* SUPERVISOR_HPP */
