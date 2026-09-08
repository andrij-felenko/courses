#include "SmartRelay.h"
#include <iostream>

SmartRelay::SmartRelay(uint8_t relayPin, uint8_t buttonPin,
                       uint32_t deadTimeMs, uint32_t debounceMs,
                       uint32_t maxOnDurationMs)
    : m_relayPin(relayPin),
      m_buttonPin(buttonPin),
      m_deadTimeMs(deadTimeMs),
      m_debounceMs(debounceMs),
      m_maxOnDurationMs(maxOnDurationMs) {}

void SmartRelay::begin() {
    // Безпечна ініціалізація пінів при подачі напруги 220 В на модуль HLK-PM01
    applyHardwarePin(false);
    transitionTo(RelayState::Off, "Старт системи");
}

void SmartRelay::applyHardwarePin(bool high) {
    // В апаратній прошивці ESP32/Arduino: digitalWrite(m_relayPin, high ? HIGH : LOW);
    std::cout << "[GPIO " << static_cast<int>(m_relayPin) << "] Рівень реле: " 
              << (high ? "HIGH (котушка 5 В заживлена)" : "LOW (контакти розімкнено)") << "\n";
}

void SmartRelay::transitionTo(RelayState newState, std::string_view reason) {
    if (m_state != newState) {
        m_state = newState;
        if (m_callback) {
            m_callback(m_state, reason);
        }
    }
}

void SmartRelay::turnOff(uint32_t nowMs) {
    m_pendingTurnOn = false;
    if (m_state == RelayState::On) {
        applyHardwarePin(false);
        m_lastSwitchTime = nowMs;
        transitionTo(RelayState::DeadTime, "Планове або захисне вимкнення");
    }
}

void SmartRelay::turnOn(uint32_t nowMs) {
    if (m_state == RelayState::Off) {
        applyHardwarePin(true);
        m_lastSwitchTime = nowMs;
        m_turnOnTime = nowMs;
        m_pendingTurnOn = false;
        transitionTo(RelayState::On, "Користувацьке увімкнення");
    } else if (m_state == RelayState::DeadTime) {
        m_pendingTurnOn = true;
        std::cout << "[SmartRelay] Захисний таймер активний. Увімкнення поставлено в чергу.\n";
    }
}

void SmartRelay::toggle(uint32_t nowMs) {
    if (m_state == RelayState::On) {
        turnOff(nowMs);
    } else {
        turnOn(nowMs);
    }
}

void SmartRelay::updateButton(bool rawPressed, uint32_t nowMs) {
    if (rawPressed != m_lastRawButton) {
        m_lastDebounceChange = nowMs;
        m_lastRawButton = rawPressed;
    }

    if ((nowMs - m_lastDebounceChange) >= m_debounceMs) {
        if (rawPressed != m_debouncedButton) {
            m_debouncedButton = rawPressed;
            if (m_debouncedButton) {
                // Фронт натискання фізичної клавіші
                toggle(nowMs);
            }
        }
    }
}

void SmartRelay::update(uint32_t nowMs) {
    // 1. Контроль захисного мертвого часу (dead-time)
    if (m_state == RelayState::DeadTime) {
        if ((nowMs - m_lastSwitchTime) >= m_deadTimeMs) {
            transitionTo(RelayState::Off, "Завершення захисного інтервалу");
            if (m_pendingTurnOn) {
                m_pendingTurnOn = false;
                turnOn(nowMs);
            }
        }
    }

    // 2. Аварійне вимкнення за максимальним часом безперервної роботи (захист від забутих приладів)
    if (m_state == RelayState::On && m_maxOnDurationMs > 0) {
        if ((nowMs - m_turnOnTime) >= m_maxOnDurationMs) {
            std::cout << "[SmartRelay] Аварійне відключення: перевищено ліміт безперервної роботи!\n";
            turnOff(nowMs);
        }
    }
}
