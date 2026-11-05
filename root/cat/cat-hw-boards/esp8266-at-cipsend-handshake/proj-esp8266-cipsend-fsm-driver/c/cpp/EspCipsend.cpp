#include "EspCipsend.hpp"
#include <cstdio>
#include <string>

EspCipsend::EspCipsend(IUart& uart) 
    : m_uart(uart), m_state(State::Idle), m_timerStart(0), m_timeoutMs(0) {}

bool EspCipsend::start(std::span<const uint8_t> payload, uint32_t timeoutMs) {
    if (m_state != State::Idle && m_state != State::Error) {
        return false;
    }

    m_payload = payload;
    m_timeoutMs = timeoutMs;
    
    // Формуємо команду з довжиною даних
    std::string cmd = "AT+CIPSEND=" + std::to_string(m_payload.size()) + "\r\n";
    m_uart.write(reinterpret_cast<const uint8_t*>(cmd.c_str()), cmd.size());
    
    m_timerStart = m_uart.getTickMs();
    m_state = State::WaitPrompt;
    
    return true;
}

void EspCipsend::tick() {
    // Перевірка таймауту
    if (m_state == State::WaitPrompt || m_state == State::WaitOk) {
        if (m_uart.getTickMs() - m_timerStart > m_timeoutMs) {
            m_state = State::Error;
            return;
        }
    }

    uint8_t c;
    switch (m_state) {
        case State::WaitPrompt:
            while (m_uart.readChar(c)) {
                if (c == '>') {
                    // Символ запрошення отримано, шлемо дані
                    m_uart.write(m_payload.data(), m_payload.size());
                    m_timerStart = m_uart.getTickMs();
                    m_state = State::WaitOk;
                    break;
                }
            }
            break;

        case State::WaitOk:
            // Чекаємо "SEND OK" (наївно чекаємо 'K' для спрощення)
            while (m_uart.readChar(c)) {
                if (c == 'K') {
                    m_state = State::Idle;
                    break;
                }
            }
            break;

        case State::Idle:
        case State::Error:
        default:
            break;
    }
}

EspCipsend::State EspCipsend::getState() const {
    return m_state;
}
