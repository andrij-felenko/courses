/* Ідіоматична C++20 архітектура моніторингу безпеки для FreeRTOS / Zephyr */
#include <array>
#include <span>
#include <atomic>

namespace embedded_rtos {

template <std::size_t Dim = 16>
class SafetyMonitorWorker final {
public:
    explicit SafetyMonitorWorker(embedded_ml::CovariateShiftDetector<64, Dim>& detector) noexcept
        : detector_(detector) {}

    void on_sensor_sample_produced(std::span<const float, Dim> features) noexcept {
        static_cast<void>(detector_.push_sample(features));
    }

    void run_audit_cycle() noexcept {
        const auto result = detector_.evaluate();
        if (result.has_value() && result->status == embedded_ml::SafetyStatus::Critical) {
            trigger_failsafe(result->mmd_squared);
        }
    }

private:
    void trigger_failsafe(float mmd_metric) noexcept {
        is_failsafe_active_.store(true, std::memory_order_release);
    }

    embedded_ml::CovariateShiftDetector<64, Dim>& detector_;
    std::atomic<bool> is_failsafe_active_{false};
};

} // namespace embedded_rtos
