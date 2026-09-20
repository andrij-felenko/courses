/**
 * @file EnablingPedal.cpp
 * @brief Реалізація об'єктно-орієнтованого класу педалі дозволу.
 */

#include "EnablingPedal.hpp"

EnablingPedal::EnablingPedal(const PedalConfig& config)
    : m_config(config) {}

void EnablingPedal::setOnStateChanged(StateCallback callback) {
    m_onStateChanged = std::move(callback);
}

void EnablingPedal::setOnFault(FaultCallback callback) {
    m_onFault = std::move(callback);
}

void EnablingPedal::setLed(LedIndicator led) noexcept {
    m_ledStatus = led;
}

void EnablingPedal::triggerFault(std::string_view reason) {
    m_state = SafetyState::Fault;
    m_requiresReset = true;
    setLed(LedIndicator::RedBlinking);

    if (m_onFault) {
        m_onFault(reason);
    }
}

void EnablingPedal::debounce(bool rawA, bool rawB, std::uint32_t currentTimeMs) {
    if (rawA != m_rawLastA) {
        m_rawLastA = rawA;
        m_lastChangeMsA = currentTimeMs;
    } else if ((currentTimeMs - m_lastChangeMsA) >= m_config.debounceMs) {
        m_debouncedA = rawA;
    }

    if (rawB != m_rawLastB) {
        m_rawLastB = rawB;
        m_lastChangeMsB = currentTimeMs;
    } else if ((currentTimeMs - m_lastChangeMsB) >= m_config.debounceMs) {
        m_debouncedB = rawB;
    }
}

void EnablingPedal::update(bool channelA, bool channelB, std::uint32_t currentTimeMs) {
    debounce(channelA, channelB, currentTimeMs);

    SafetyState previousState = m_state;

    // Перевірка часового розсуву між двома каналами (discrepancy check)
    if (m_debouncedA != m_debouncedB) {
        if (!m_discrepancyActive) {
            m_discrepancyActive = true;
            m_discrepancyStartMs = currentTimeMs;
        } else if ((currentTimeMs - m_discrepancyStartMs) >= m_config.discrepancyTimeoutMs) {
            triggerFault("Розсинхронізація каналів безпеки (discrepancy timeout)");
            return;
        }
    } else {
        m_discrepancyActive = false;
    }

    // Автомат станів (FSM)
    if (!m_debouncedA && !m_debouncedB) {
        // Положення 1: Педаль відпущена
        if (m_requiresReset) {
            m_requiresReset = false;
        }
        m_state = SafetyState::Released;
        setLed(LedIndicator::Off);
    } else if (m_debouncedA && m_debouncedB) {
        // Затиснуто обидва канали
        if (m_requiresReset) {
            m_state = SafetyState::Fault;
            setLed(LedIndicator::Yellow);
        } else {
            if (m_state != SafetyState::Enabled) {
                m_enabledStartMs = currentTimeMs;
            }
            // Перевірка заклинювання або тривалого неперервного затискання педалі
            if ((currentTimeMs - m_enabledStartMs) >= m_config.maxStuckTimeMs) {
                triggerFault("Перевищено максимальний час неперервного затискання педалі (заклинювання)");
                return;
            }
            m_state = SafetyState::Enabled;
            setLed(LedIndicator::Green);
        }
    }

    if (m_state != previousState && m_onStateChanged) {
        m_onStateChanged(m_state);
    }
}

void EnablingPedal::reset() {
    if (m_state == SafetyState::Released) {
        m_requiresReset = false;
        m_discrepancyActive = false;
        setLed(LedIndicator::Off);
    }
}

std::string_view EnablingPedal::stateToString(SafetyState state) noexcept {
    switch (state) {
        case SafetyState::Released: return "Released (Вимкнено)";
        case SafetyState::Enabled:  return "Enabled (Дозвіл)";
        case SafetyState::Panic:    return "Panic (Паніка)";
        case SafetyState::Fault:    return "Fault (Аварія)";
    }
    return "Unknown";
}
