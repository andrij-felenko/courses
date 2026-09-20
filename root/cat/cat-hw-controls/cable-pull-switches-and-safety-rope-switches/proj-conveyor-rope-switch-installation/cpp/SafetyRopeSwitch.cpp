#include "SafetyRopeSwitch.h"

SafetyRopeSwitch::SafetyRopeSwitch(const SafetyRopeSwitchConfig& config)
    : m_config(config),
      m_state(SafetyState::SYSTEM_OK),
      m_ch1Raw(false),
      m_ch2Raw(false),
      m_ch1Stable(false),
      m_ch2Stable(false),
      m_ch1LastChangeMs(0),
      m_ch2LastChangeMs(0),
      m_discrepancyStartMs(0),
      m_discrepancyTimingActive(false) {
}

void SafetyRopeSwitch::begin() {
    // Налаштування пінів вводу з внутрішньою підтяжкою PULLUP
    // Низький рівень (LOW) = контакт замкнений (Нормальний натяг троса)
    // Високий рівень (HIGH) = контакт розімкнений (Натяг / Обрив / Спрацьовування)
    pinMode(m_config.ch1Pin, INPUT_PULLUP);
    pinMode(m_config.ch2Pin, INPUT_PULLUP);
    pinMode(m_config.resetPin, INPUT_PULLUP);

    uint32_t now = millis();
    bool r1 = (digitalRead(m_config.ch1Pin) == LOW);
    bool r2 = (digitalRead(m_config.ch2Pin) == LOW);

    m_ch1Raw = r1;
    m_ch2Raw = r2;
    m_ch1Stable = r1;
    m_ch2Stable = r2;
    m_ch1LastChangeMs = now;
    m_ch2LastChangeMs = now;

    if (!r1 || !r2) {
        m_state = SafetyState::TRIPPED_ALARM;
    } else {
        m_state = SafetyState::SYSTEM_OK;
    }
}

void SafetyRopeSwitch::processDebounce() {
    uint32_t now = millis();

    // Читання вхідних рівнів: LOW означає нормально замкнений контакт (ОК)
    bool r1 = (digitalRead(m_config.ch1Pin) == LOW);
    bool r2 = (digitalRead(m_config.ch2Pin) == LOW);

    if (r1 != m_ch1Raw) {
        m_ch1Raw = r1;
        m_ch1LastChangeMs = now;
    } else if ((now - m_ch1LastChangeMs) >= m_config.debounceMs) {
        m_ch1Stable = m_ch1Raw;
    }

    if (r2 != m_ch2Raw) {
        m_ch2Raw = r2;
        m_ch2LastChangeMs = now;
    } else if ((now - m_ch2LastChangeMs) >= m_config.debounceMs) {
        m_ch2Stable = m_ch2Raw;
    }
}

void SafetyRopeSwitch::processDiscrepancy() {
    uint32_t now = millis();

    // Якщо обидва канали розімкнені (!m_ch1Stable && !m_ch2Stable) — це явна аварія (трос висмикнуто або розірвано)
    if (!m_ch1Stable && !m_ch2Stable) {
        m_discrepancyTimingActive = false;
        m_state = SafetyState::TRIPPED_ALARM;
        return;
    }

    // Якщо один канал замкнений, а інший розімкнений — фіксуємо розбіжність
    if (m_ch1Stable != m_ch2Stable) {
        if (!m_discrepancyTimingActive) {
            m_discrepancyTimingActive = true;
            m_discrepancyStartMs = now;
        } else if ((now - m_discrepancyStartMs) >= m_config.discrepancyTimeoutMs) {
            // Час розбіжності перевищено — фіксуємо апаратну несправність каналів (FAULT)
            m_state = SafetyState::FAULT_DISCREPANCY;
        }
    } else {
        m_discrepancyTimingActive = false;
    }
}

void SafetyRopeSwitch::update() {
    processDebounce();

    // Кінцевий автомат станів безпеки
    switch (m_state) {
    case SafetyState::SYSTEM_OK:
        processDiscrepancy();
        break;

    case SafetyState::TRIPPED_ALARM:
        // Якщо обидва канали повернулися в норму, переходимо в режим очікування скиду
        if (m_ch1Stable && m_ch2Stable) {
            m_state = SafetyState::WAITING_FOR_RESET;
        }
        break;

    case SafetyState::FAULT_DISCREPANCY:
        // У разі апаратної несправності вихід із блокування можливий лише після усунення розбіжності
        if (m_ch1Stable && m_ch2Stable) {
            m_state = SafetyState::WAITING_FOR_RESET;
        }
        break;

    case SafetyState::WAITING_FOR_RESET:
        // Якщо під час очікування скиду один із каналів знову відкриється, повертаємось в аварію
        if (!m_ch1Stable || !m_ch2Stable) {
            m_state = SafetyState::TRIPPED_ALARM;
        } else {
            // Перевіряємо натискання кнопки Reset (активний низький рівень LOW)
            if (digitalRead(m_config.resetPin) == LOW) {
                reset();
            }
        }
        break;
    }
}

bool SafetyRopeSwitch::reset() {
    // Скид дозволений лише тоді, коли обидва канали безпеки знаходяться у стабільно замкненому стані
    if (m_ch1Stable && m_ch2Stable && (m_state == SafetyState::WAITING_FOR_RESET || m_state == SafetyState::TRIPPED_ALARM)) {
        m_state = SafetyState::SYSTEM_OK;
        m_discrepancyTimingActive = false;
        return true;
    }
    return false;
}

SafetyState SafetyRopeSwitch::getState() const {
    return m_state;
}

bool SafetyRopeSwitch::isSystemOk() const {
    return (m_state == SafetyState::SYSTEM_OK);
}

const char* SafetyRopeSwitch::getStateName() const {
    switch (m_state) {
    case SafetyState::SYSTEM_OK:
        return "СИСТЕМА В НОРМІ (RUN)";
    case SafetyState::TRIPPED_ALARM:
        return "АВАРІЙНЕ ЗУПИНЕННЯ (TRIPPED)";
    case SafetyState::FAULT_DISCREPANCY:
        return "АПАРАТНА НЕСПРАВНІСТЬ КАНАЛІВ (FAULT)";
    case SafetyState::WAITING_FOR_RESET:
        return "ОЧІКУВАННЯ НАТИСКАННЯ КНОПКИ RESET";
    default:
        return "НЕВІДОМИЙ СТАН";
    }
}
