// ============================================================================
// C++20 Модуль диспетчеризації захисту силового H-моста
// ============================================================================

#include <cstdint>
#include <chrono>
#include <concepts>
#include <atomic>

class HBridgeDesatGuard {
public:
    enum class SystemState : uint8_t {
        Disabled,
        Running,
        FaultTripped,
        PermanentLockout
    };

    struct Settings {
        uint32_t maxRetryAttempts{3};
        std::chrono::milliseconds cooldownDuration{3000};
        bool autoResetAllowed{true};
    };

    explicit HBridgeDesatGuard(const Settings& settings) noexcept
        : settings_(settings), state_(SystemState::Disabled), faultCounter_(0) {}

    // Обробка апаратного переривання від піна FAULT
    void handleFaultInterrupt(uint32_t currentTickMs) noexcept {
        state_.store(SystemState::FaultTripped, std::memory_order_release);
        faultCounter_++;
        lastFaultTimestampMs_ = currentTickMs;
        
        hardwareEmergencyMute();
    }

    // Регулярний моніторинг стану
    void process(uint32_t currentTickMs) noexcept {
        auto currentState = state_.load(std::memory_order_acquire);
        if (currentState != SystemState::FaultTripped) {
            return;
        }

        if (faultCounter_ >= settings_.maxRetryAttempts) {
            state_.store(SystemState::PermanentLockout, std::memory_order_release);
            return;
        }

        if (settings_.autoResetAllowed) {
            auto elapsed = currentTickMs - lastFaultTimestampMs_;
            if (elapsed >= settings_.cooldownDuration.count()) {
                if (isHardwareReady()) {
                    pulseResetPin();
                    state_.store(SystemState::Disabled, std::memory_order_release);
                }
            }
        }
    }

    [[nodiscard]] SystemState getState() const noexcept {
        return state_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] uint32_t getFaultCount() const noexcept {
        return faultCounter_;
    }

private:
    void hardwareEmergencyMute() noexcept {
        // Пряма модифікація регістрів таймера ШІМ
    }

    [[nodiscard]] bool isHardwareReady() const noexcept {
        // Перевірка логічного рівня лінії FAULT
        return true;
    }

    void pulseResetPin() noexcept {
        // Формування імпульсу скидання тригера аварії на драйвері
    }

    Settings settings_;
    std::atomic<SystemState> state_;
    uint32_t faultCounter_;
    uint32_t lastFaultTimestampMs_{0};
};
