// supervisor.hpp — та сама бізнес-логіка, що й у C, але залежність
// приходить посиланням на інтерфейс: ані NULL, ані дірки в таблиці.
#pragma once

#include "board.hpp"

#include <chrono>
#include <cstdint>
#include <optional>

namespace app {

using namespace std::chrono_literals;

inline constexpr std::uint16_t kVbatWarningMv = 3300;
inline constexpr std::uint16_t kVbatCriticalMv = 3000;
inline constexpr std::chrono::milliseconds kSensorSettle = 15ms;
inline constexpr std::chrono::milliseconds kRetryPause = 5ms;
inline constexpr unsigned kEnvAttempts = 3;
inline constexpr std::chrono::milliseconds kDeepSleep = std::chrono::hours(1);
inline constexpr std::chrono::milliseconds kCyclePeriod = 60s;

class SystemSupervisor {
public:
    explicit SystemSupervisor(bsp::IBoardSupport& board) noexcept : bsp_(board) {}

    void run_cycle() noexcept;

    [[nodiscard]] bool is_low_power_warning() const noexcept { return low_power_warning_; }
    [[nodiscard]] bool is_critical_shutdown() const noexcept { return critical_shutdown_; }
    [[nodiscard]] bool has_fresh_env() const noexcept { return fresh_env_; }
    [[nodiscard]] const std::optional<bsp::EnvironmentMetrics>& last_env() const noexcept {
        return last_env_;
    }
    [[nodiscard]] unsigned env_fault_count() const noexcept { return env_faults_; }
    [[nodiscard]] unsigned battery_fault_count() const noexcept { return battery_faults_; }
    [[nodiscard]] unsigned cycles() const noexcept { return cycles_; }

private:
    std::expected<bsp::EnvironmentMetrics, bsp::Status> read_env_retrying() noexcept;

    bsp::IBoardSupport& bsp_;
    std::optional<bsp::EnvironmentMetrics> last_env_{};
    bool low_power_warning_{false};
    bool critical_shutdown_{false};
    bool fresh_env_{false};
    unsigned env_faults_{0};
    unsigned battery_faults_{0};
    unsigned cycles_{0};
};

} // namespace app
