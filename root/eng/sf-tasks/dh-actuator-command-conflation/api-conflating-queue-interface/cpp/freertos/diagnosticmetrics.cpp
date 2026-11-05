#include <cstdint>
#include <atomic>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace Diagnostic {

struct DiagnosticMetrics {
    std::atomic<uint32_t> receivedCommands{0};
    std::atomic<uint32_t> committedCommands{0};
};

class TelemetryActuatorController {
public:
    void pushSetpoint(uint16_t val) {
        metrics_.receivedCommands.fetch_add(1, std::memory_order_relaxed);
        setpoint_.store(val, std::memory_order_relaxed);
        pendingFlag_.store(true, std::memory_order_release);
    }

    void pushEmergencyStop() {
        metrics_.receivedCommands.fetch_add(1, std::memory_order_relaxed);
        emergencyState_.store(true, std::memory_order_release);
        
        // Негайне аварійне вимкнення виходу периферії
        portENTER_CRITICAL();
        // TIM1->CCR1 = 0;
        portEXIT_CRITICAL();
    }

    void updateDriver() {
        if (emergencyState_.load(std::memory_order_acquire)) {
            // Режим аварійного блокування
            return;
        }

        if (pendingFlag_.exchange(false, std::memory_order_acq_rel)) {
            uint16_t target = setpoint_.load(std::memory_order_relaxed);
            metrics_.committedCommands.fetch_add(1, std::memory_order_relaxed);
            
            // Запис у регістри мікроконтролера
            // TIM1->CCR1 = target;
        }
    }

    float calculateConflationRatio() const {
        uint32_t rx = metrics_.receivedCommands.load(std::memory_order_relaxed);
        uint32_t tx = metrics_.committedCommands.load(std::memory_order_relaxed);
        if (rx == 0) return 0.0f;
        return static_cast<float>(rx - tx) / static_cast<float>(rx);
    }

private:
    std::atomic<uint16_t> setpoint_{0};
    std::atomic<bool>     pendingFlag_{false};
    std::atomic<bool>     emergencyState_{false};
    DiagnosticMetrics     metrics_;
};

} // namespace Diagnostic
