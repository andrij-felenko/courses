/* stm32_supervisor.hpp — Ідіоматична C++ реалізація */
#pragma once
#include "main.h"
#include <cstdint>
#include <atomic>
#include <concepts>

namespace SystemSafety {

enum class TaskId : uint32_t {
    Sensor  = (1U << 0),
    Control = (1U << 1),
    Comms   = (1U << 2)
};

class SupervisorController {
public:
    static constexpr uint32_t RequiredMask = 
        static_cast<uint32_t>(TaskId::Sensor) |
        static_cast<uint32_t>(TaskId::Control) |
        static_cast<uint32_t>(TaskId::Comms);

    static constexpr uint32_t MinWindowMs = 45;
    static constexpr uint32_t MaxWindowMs = 75;

    static void reportTask(TaskId id) noexcept {
        healthFlags_.fetch_or(static_cast<uint32_t>(id), std::memory_order_relaxed);
    }

    static void handlePowerFailIsr() noexcept {
        powerFailState_.store(true, std::memory_order_seq_cst);
        HAL_GPIO_WritePin(PERIPH_PWR_EN_GPIO_Port, PERIPH_PWR_EN_Pin, GPIO_PIN_RESET);
        saveEmergencyState();
    }

    static void serviceWatchdog(uint32_t currentTickMs) noexcept {
        if (powerFailState_.load(std::memory_order_relaxed)) {
            return;
        }

        const uint32_t delta = currentTickMs - lastKickMs_;
        if (delta >= MinWindowMs && delta <= MaxWindowMs) {
            uint32_t expected = RequiredMask;
            if (healthFlags_.compare_exchange_strong(expected, 0, std::memory_order_acq_rel)) {
                HAL_GPIO_TogglePin(WDI_GPIO_Port, WDI_Pin);
                lastKickMs_ = currentTickMs;
            }
        }
    }

private:
    static inline std::atomic<uint32_t> healthFlags_{0};
    static inline std::atomic<bool> powerFailState_{false};
    static inline uint32_t lastKickMs_{0};

    static void saveEmergencyState() noexcept;
};

} // namespace SystemSafety
