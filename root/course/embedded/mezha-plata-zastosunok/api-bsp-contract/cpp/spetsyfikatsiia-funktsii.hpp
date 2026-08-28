#ifndef BSP_INTERFACE_HPP
#define BSP_INTERFACE_HPP

#include "bsp_types.hpp"
#include <expected>
#include <chrono>

namespace bsp {

/**
 * @brief Абстрактний інтерфейс пакету підтримки плати для C++.
 */
class IBoardSupport {
public:
    virtual ~IBoardSupport() = default;

    [[nodiscard]] virtual Status init() noexcept = 0;
    [[nodiscard]] virtual Status deinit() noexcept = 0;

    [[nodiscard]] virtual Status led_set(LedId led, LedState state) noexcept = 0;
    [[nodiscard]] virtual Status led_toggle(LedId led) noexcept = 0;

    [[nodiscard]] virtual Status power_domain_set(PowerDomain domain, bool enable) noexcept = 0;

    [[nodiscard]] virtual std::expected<BatteryMetrics, Status> get_battery_metrics() noexcept = 0;
    [[nodiscard]] virtual std::expected<EnvironmentMetrics, Status> read_environment() noexcept = 0;

    [[nodiscard]] virtual Status enter_low_power(SleepMode mode, std::chrono::milliseconds timeout) noexcept = 0;
    [[nodiscard]] virtual std::chrono::milliseconds get_uptime() const noexcept = 0;
    virtual void delay(std::chrono::microseconds us) const noexcept = 0;
};

/**
 * @brief RAII-обгортка для автоматичного знеструмлення периферійного домену.
 */
class [[nodiscard]] PowerDomainGuard {
public:
    PowerDomainGuard(IBoardSupport& bsp, PowerDomain domain)
        : bsp_(bsp), domain_(domain), active_(false) {
        if (bsp_.power_domain_set(domain_, true) == Status::Ok) {
            active_ = true;
        }
    }

    ~PowerDomainGuard() {
        if (active_) {
            bsp_.power_domain_set(domain_, false);
        }
    }

    [[nodiscard]] bool is_active() const noexcept { return active_; }

    PowerDomainGuard(const PowerDomainGuard&) = delete;
    PowerDomainGuard& operator=(const PowerDomainGuard&) = delete;
    PowerDomainGuard(PowerDomainGuard&&) noexcept = default;

private:
    IBoardSupport& bsp_;
    PowerDomain domain_;
    bool active_;
};

} // namespace bsp

#endif /* BSP_INTERFACE_HPP */
