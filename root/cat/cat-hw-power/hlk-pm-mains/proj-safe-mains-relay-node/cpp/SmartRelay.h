#pragma once

#include <cstdint>
#include <functional>
#include <string_view>

/**
 * @brief Стани життєвого циклу розумного реле
 */
enum class RelayState {
    Off,         // Навантаження відключене
    On,          // Навантаження під напругою
    DeadTime,    // Захисний інтервал між вимкненням і увімкненням
    Fault        // Аварійний стан (перегрів або залипання контактів)
};

/**
 * @brief Тип функції зворотного виклику для сповіщення про зміну стану
 */
using StateChangeCallback = std::function<void(RelayState newState, std::string_view reason)>;

/**
 * @brief Клас захищеного комутатора для мережевих вузлів на базі HLK-PM01
 */
class SmartRelay {
public:
    SmartRelay(uint8_t relayPin, uint8_t buttonPin, 
               uint32_t deadTimeMs = 3000, 
               uint32_t debounceMs = 40,
               uint32_t maxOnDurationMs = 0);

    void begin();
    void turnOn(uint32_t nowMs);
    void turnOff(uint32_t nowMs);
    void toggle(uint32_t nowMs);

    void updateButton(bool rawPressed, uint32_t nowMs);
    void update(uint32_t nowMs);

    void onStateChanged(StateChangeCallback cb) { m_callback = std::move(cb); }
    [[nodiscard]] RelayState getState() const no_index { return m_state; }
    [[nodiscard]] bool isActive() const { return m_state == RelayState::On; }

private:
    void applyHardwarePin(bool high);
    void transitionTo(RelayState newState, std::string_view reason);

    uint8_t m_relayPin;
    uint8_t m_buttonPin;
    uint32_t m_deadTimeMs;
    uint32_t m_debounceMs;
    uint32_t m_maxOnDurationMs; // 0 = без обмеження

    RelayState m_state{RelayState::Off};
    bool m_pendingTurnOn{false};

    uint32_t m_lastSwitchTime{0};
    uint32_t m_turnOnTime{0};

    // Фільтрація брязкання контактів
    bool m_lastRawButton{false};
    bool m_debouncedButton{false};
    uint32_t m_lastDebounceChange{0};

    StateChangeCallback m_callback{nullptr};
};
