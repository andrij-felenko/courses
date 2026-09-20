#include "cable_pull_switch.hpp"

CablePullSwitch::CablePullSwitch(const Config& config)
    : m_config(config) {}

void CablePullSwitch::updateChannelDebounce(ChannelDebounce& channel, bool raw_input, uint32_t now_ms) {
    if (raw_input != channel.raw_state) {
        channel.raw_state = raw_input;
        channel.last_change_ms = now_ms;
    } else if ((now_ms - channel.last_change_ms) >= m_config.debounce_ms) {
        channel.stable_state = channel.raw_state;
    }
}

void CablePullSwitch::update(uint32_t now_ms, bool raw_nc1, bool raw_nc2) {
    // 1. Фільтрація дребезгу для кожного з двох NC-каналів
    updateChannelDebounce(m_ch1, raw_nc1, now_ms);
    updateChannelDebounce(m_ch2, raw_nc2, now_ms);

    const bool nc1_closed = m_ch1.stable_state;
    const bool nc2_closed = m_ch2.stable_state;

    // 2. Аналіз розсинхронізації сигналів між каналами
    const bool in_sync = (nc1_closed == nc2_closed);

    if (!in_sync) {
        if (!m_discrepancy_timer_active) {
            m_discrepancy_timer_active = true;
            m_discrepancy_start_ms = now_ms;
        } else if ((now_ms - m_discrepancy_start_ms) > m_config.max_discrepancy_ms) {
            // Перевищено таймаут неузгодженості -> апаратний дефект (заліпання/обрив одного з контактів)
            m_state = State::DiscrepancyFault;
        }
    } else {
        m_discrepancy_timer_active = false;
    }

    // 3. Переходи скінченного автомата (FSM)
    switch (m_state) {
        case State::Normal:
            if (!nc1_closed && !nc2_closed) {
                // Обидва контакти розімкнено -> миттєве аварійне зупинення
                m_state = State::EmergencyStop;
            }
            break;

        case State::EmergencyStop:
            if (nc1_closed && nc2_closed && !m_discrepancy_timer_active) {
                // Трос натягнуто, контакти замкнено -> перехід у заблокований стан до ручного скидання
                m_state = State::WaitForReset;
            }
            break;

        case State::WaitForReset:
            if (!nc1_closed || !nc2_closed) {
                // Повторне порушення натягу до виконання reset -> повернення в аварію
                m_state = State::EmergencyStop;
            }
            break;

        case State::DiscrepancyFault:
            // Фатальна помилка обладнання: вихід лише через ручне скидання при замкнених контактах
            break;
    }
}

bool CablePullSwitch::reset() {
    // Згідно з IEC 60947-5-5, скидання можливе тільки якщо контакти фізично відновлено
    if ((m_state == State::WaitForReset || m_state == State::DiscrepancyFault) &&
        m_ch1.stable_state && m_ch2.stable_state && !m_discrepancy_timer_active) {
        m_state = State::Normal;
        return true;
    }
    return false;
}
