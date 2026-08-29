// board.hpp — контракт плати мовою C++: інтерфейс замість таблиці покажчиків.
//
// Помилку несе std::expected, тривалості — std::chrono, а не «мілісекунди
// в uint32_t». Знеструмлення домену гарантує RAII, а не парний виклик руками.
#pragma once

#include <chrono>
#include <cstdint>
#include <expected>

namespace bsp {

enum class Status { Ok, InvalidParam, Unsupported, Timeout, BusFault };
enum class LedId { SystemStatus, Warning };
enum class LedState { Off, On };
enum class PowerDomain { Sensors, Radio };
enum class SleepMode { Light, Deep };

struct BatteryMetrics {
    std::uint16_t voltage_mv{};
    std::uint8_t charge_percent{};
};

struct EnvironmentMetrics {
    std::int16_t temperature_centi_c{};
    std::chrono::milliseconds timestamp{};
};

class IBoardSupport {
public:
    virtual ~IBoardSupport() = default;

    virtual Status led_set(LedId led, LedState state) noexcept = 0;
    virtual Status power_domain_set(PowerDomain domain, bool enable) noexcept = 0;
    virtual std::expected<BatteryMetrics, Status> get_battery_metrics() noexcept = 0;
    virtual std::expected<EnvironmentMetrics, Status> read_environment() noexcept = 0;
    virtual Status enter_low_power(SleepMode mode, std::chrono::milliseconds timeout) noexcept = 0;
    virtual void delay(std::chrono::milliseconds duration) noexcept = 0;
    [[nodiscard]] virtual std::chrono::milliseconds uptime() const noexcept = 0;
};

// Вмикає домен, витримує паузу стабілізації й гарантовано знеструмлює його
// на виході з області видимості — хоч через return, хоч через три збої шини.
class PowerDomainGuard {
public:
    PowerDomainGuard(IBoardSupport& bsp, PowerDomain domain,
                     std::chrono::milliseconds settle) noexcept
        : bsp_(bsp), domain_(domain) {
        active_ = (bsp_.power_domain_set(domain_, true) == Status::Ok);
        if (active_ && settle.count() > 0) {
            bsp_.delay(settle);
        }
    }

    ~PowerDomainGuard() noexcept {
        if (active_) {
            bsp_.power_domain_set(domain_, false);
        }
    }

    PowerDomainGuard(const PowerDomainGuard&) = delete;
    PowerDomainGuard& operator=(const PowerDomainGuard&) = delete;

    [[nodiscard]] bool is_active() const noexcept { return active_; }

private:
    IBoardSupport& bsp_;
    PowerDomain domain_;
    bool active_{false};
};

} // namespace bsp
