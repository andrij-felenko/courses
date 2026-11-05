#pragma once

#include "IUart.hpp"
#include <span>

class EspCipsend {
public:
    enum class State {
        Idle,
        WaitPrompt,
        WaitOk,
        Error
    };

    explicit EspCipsend(IUart& uart);

    // Запуск передачі, використовуємо std::span для безпечного доступу до буфера
    bool start(std::span<const uint8_t> payload, uint32_t timeoutMs);

    // Оновлення стану (викликається в головному циклі)
    void tick();

    State getState() const;

private:
    IUart& m_uart;
    State m_state;
    std::span<const uint8_t> m_payload;
    uint32_t m_timerStart;
    uint32_t m_timeoutMs;
};
