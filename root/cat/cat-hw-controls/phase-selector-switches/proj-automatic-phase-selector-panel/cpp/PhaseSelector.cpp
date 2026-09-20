#include "PhaseSelector.h"

PhaseSelector::PhaseSelector(const PhaseConfig& config)
    : m_config(config) {
}

PhaseSelector::~PhaseSelector() = default;

void PhaseSelector::begin() {
    // Конфігурація виходів керування реле
    pinMode(m_config.pinRelayL1, OUTPUT);
    pinMode(m_config.pinRelayL2, OUTPUT);
    pinMode(m_config.pinRelayL3, OUTPUT);

    // Гарантоване початкове програмне та апаратне вимкнення усіх силових каналів
    setRelaysHardware(PhaseId::NONE);

    // Вимірювання первинних напруг
    measureVoltages();
}

void PhaseSelector::measureVoltages() {
    // Зчитання АЦП та переведення в RMS напругу (В)
    m_voltages[static_cast<uint8_t>(PhaseId::L1)] = analogRead(m_config.pinVoltL1) * m_config.voltageScaleFactor;
    m_voltages[static_cast<uint8_t>(PhaseId::L2)] = analogRead(m_config.pinVoltL2) * m_config.voltageScaleFactor;
    m_voltages[static_cast<uint8_t>(PhaseId::L3)] = analogRead(m_config.pinVoltL3) * m_config.voltageScaleFactor;

    // Оновлення статусу кожної фази з урахуванням гістерезису
    for (uint8_t i = 1; i <= 3; ++i) {
        float v = m_voltages[i];
        bool currentOk = m_phaseOk[i];

        if (currentOk) {
            // Вихід із норми відбуваються миттєво при виході за межі [uMin, uMax]
            if (v < m_config.uMin || v > m_config.uMax) {
                m_phaseOk[i] = false;
            }
        } else {
            // Повернення у норму потребує входу в звужений діапазон із гістерезисом
            if (v >= (m_config.uMin + m_config.uHysteresis) && v <= (m_config.uMax - m_config.uHysteresis)) {
                m_phaseOk[i] = true;
            }
        }
    }
}

PhaseId PhaseSelector::selectBestAvailablePhase() const {
    // Пріоритет фаз: L1 -> L2 -> L3
    if (m_phaseOk[static_cast<uint8_t>(PhaseId::L1)]) return PhaseId::L1;
    if (m_phaseOk[static_cast<uint8_t>(PhaseId::L2)]) return PhaseId::L2;
    if (m_phaseOk[static_cast<uint8_t>(PhaseId::L3)]) return PhaseId::L3;
    return PhaseId::NONE;
}

void PhaseSelector::setRelaysHardware(PhaseId activePhase) {
    // Суворе взаємне блокування: спочатку повністю вимикаємо всі реле
    digitalWrite(m_config.pinRelayL1, LOW);
    digitalWrite(m_config.pinRelayL2, LOW);
    digitalWrite(m_config.pinRelayL3, LOW);

    // Умикаємо лише одне вибране реле
    switch (activePhase) {
        case PhaseId::L1:
            digitalWrite(m_config.pinRelayL1, HIGH);
            break;
        case PhaseId::L2:
            digitalWrite(m_config.pinRelayL2, HIGH);
            break;
        case PhaseId::L3:
            digitalWrite(m_config.pinRelayL3, HIGH);
            break;
        case PhaseId::NONE:
        default:
            break;
    }
}

void PhaseSelector::update() {
    uint32_t now = millis();
    measureVoltages();

    PhaseId bestPhase = selectBestAvailablePhase();

    switch (m_state) {
        case ControllerState::ALL_OFF:
            if (bestPhase != PhaseId::NONE) {
                m_targetPhase = bestPhase;
                m_state = ControllerState::DEAD_TIME;
                m_stateTimer = now;
            }
            break;

        case ControllerState::ACTIVE:
            // Аварія поточної фази — негайне вимкнення та перехід у dead-time
            if (!isPhaseValid(m_activePhase)) {
                setRelaysHardware(PhaseId::NONE);
                m_activePhase = PhaseId::NONE;
                m_targetPhase = bestPhase;
                m_state = ControllerState::DEAD_TIME;
                m_stateTimer = now;
            }
            // Якщо ми живимося не від L1, а L1 відновилася — запускаємо таймер затримки повернення
            else if (m_activePhase != PhaseId::L1 && isPhaseValid(PhaseId::L1)) {
                m_targetPhase = PhaseId::L1;
                m_state = ControllerState::RETURN_DELAY;
                m_returnTimer = now;
            }
            break;

        case ControllerState::RETURN_DELAY:
            // Якщо за час відліку L1 знову вийшла з ладу — скасовуємо повернення
            if (!isPhaseValid(PhaseId::L1)) {
                m_state = ControllerState::ACTIVE;
            }
            // Якщо пріоритетна L1 стабільна протягом returnDelayMs — ініціюємо перемикання
            else if ((now - m_returnTimer) >= m_config.returnDelayMs) {
                setRelaysHardware(PhaseId::NONE);
                m_activePhase = PhaseId::NONE;
                m_targetPhase = PhaseId::L1;
                m_state = ControllerState::DEAD_TIME;
                m_stateTimer = now;
            }
            break;

        case ControllerState::DEAD_TIME:
            // Захисна дугова пауза між перемиканнями силових реле
            if ((now - m_stateTimer) >= m_config.deadTimeMs) {
                if (isPhaseValid(m_targetPhase)) {
                    m_activePhase = m_targetPhase;
                    setRelaysHardware(m_activePhase);
                    m_state = ControllerState::ACTIVE;
                } else {
                    // Якщо за час dead-time цільова фаза зіпсована — вибираємо знову
                    if (bestPhase != PhaseId::NONE) {
                        m_targetPhase = bestPhase;
                        m_stateTimer = now;
                    } else {
                        m_state = ControllerState::ALL_OFF;
                    }
                }
            }
            break;
    }
}

PhaseId PhaseSelector::getActivePhase() const {
    return m_activePhase;
}

float PhaseSelector::getVoltage(PhaseId phase) const {
    uint8_t idx = static_cast<uint8_t>(phase);
    if (idx >= 1 && idx <= 3) return m_voltages[idx];
    return 0.0f;
}

bool PhaseSelector::isPhaseValid(PhaseId phase) const {
    uint8_t idx = static_cast<uint8_t>(phase);
    if (idx >= 1 && idx <= 3) return m_phaseOk[idx];
    return false;
}

ControllerState PhaseSelector::getState() const {
    return m_state;
}
