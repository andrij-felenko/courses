#include <cstdint>
#include <concepts>
#include <chrono>

extern void platform_delay_us(uint32_t us) noexcept;
extern bool i2c_hardware_bus_recover() noexcept;

template <typename TransferFn>
requires requires(TransferFn fn) { { fn() } -> std::same_as<DriverStatus>; }
class ResilientExecutor {
public:
    static DriverStatus execute(
        CircuitBreaker& cb,
        RetryPolicy& retry_policy,
        TransferFn&& transfer_fn
    ) noexcept {
        if (!cb.allow_transaction()) {
            return DriverStatus::BusTimeout;
        }

        DriverStatus status = DriverStatus::Ok;
        const uint8_t max_tries = retry_policy.max_attempts();

        for (uint8_t attempt = 1; attempt <= max_tries; ++attempt) {
            status = transfer_fn();

            if (status == DriverStatus::Ok) {
                cb.report_success();
                return DriverStatus::Ok;
            }

            const ErrorAction action = classify_error(status);

            if (action == ErrorAction::CircuitBreakerHit) {
                cb.report_failure();
                return status;
            }

            if (action == ErrorAction::BusRecover) {
                i2c_hardware_bus_recover();
            }

            if (attempt < max_tries) {
                const uint32_t delay_us = retry_policy.calculate_delay_us(attempt);
                platform_delay_us(delay_us);
            }
        }

        cb.report_failure();
        return status;
    }
};
