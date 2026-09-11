#include <cstdint>
#include <atomic>

// Бітові прапорці причин виникнення аварійних станів
namespace LaserFault {
    constexpr uint32_t NONE             = 0;
    constexpr uint32_t WATCHDOG_TIMEOUT = (1 << 0); // Перевищення часу увімкнення
    constexpr uint32_t OVERHEAT         = (1 << 1); // Критичний перегрів корпусу/діода
    constexpr uint32_t SYNC_LOST        = (1 << 2); // Порушення синхронізації з камерою
}

enum class DriverState : uint8_t {
    Init,
    Ready,
    Emitting,
    FaultLockout
};

class LaserStateMachine {
public:
    LaserStateMachine()
        : state_(DriverState::Init),
          fault_flags_(LaserFault::NONE),
          current_temp_celsius_(25.0f) {}

    // Спроба переходу в стан випромінювання (стробу)
    bool request_emission() {
        // У стані аварійного блокування будь-яке випромінювання категорично заборонено
        if (state_.load(std::memory_order_acquire) != DriverState::Ready) {
            return false;
        }

        state_.store(DriverState::Emitting, std::memory_order_release);
        return true;
    }

    // Штатне завершення випромінювання за сигналом закінчення експозиції
    void finish_emission() {
        DriverState expected = DriverState::Emitting;
        state_.compare_exchange_strong(expected, DriverState::Ready,
                                       std::memory_order_acq_rel);
    }

    // Аварійний перехід у FAULT_LOCKOUT з фіксацією бітових прапорців
    void trigger_fault(uint32_t fault_flag) {
        fault_flags_.fetch_or(fault_flag, std::memory_order_release);
        state_.store(DriverState::FaultLockout, std::memory_order_release);
    }

    // Процедура захищеного скидання блокування (failsafe reset)
    bool failsafe_reset() {
        if (state_.load(std::memory_order_acquire) != DriverState::FaultLockout) {
            // Скидання потрібне лише у стані блокування
            return false;
        }

        // Крок 1: Апаратна діагностика умов безпеки
        // Перевірка температури (поріг остигання +40 °C після перегріву +50 °C)
        if (current_temp_celsius_ >= 40.0f) {
            // Охолодження ще не настало; вихід з блокування заборонено
            return false;
        }

        // Крок 2: Очищення прапорців аварій
        fault_flags_.store(LaserFault::NONE, std::memory_order_release);

        // Крок 3: Перехід через стан Init у стан Ready
        state_.store(DriverState::Init, std::memory_order_release);
        // Завершення реініціалізації
        state_.store(DriverState::Ready, std::memory_order_release);

        return true;
    }

    DriverState get_state() const {
        return state_.load(std::memory_order_acquire);
    }

    uint32_t get_fault_flags() const {
        return fault_flags_.load(std::memory_order_acquire);
    }

    void update_temperature(float temp_celsius) {
        current_temp_celsius_ = temp_celsius;
        if (temp_celsius >= 50.0f) {
            trigger_fault(LaserFault::OVERHEAT);
        }
    }

private:
    std::atomic<DriverState> state_;
    std::atomic<uint32_t> fault_flags_;
    float current_temp_celsius_;
};
