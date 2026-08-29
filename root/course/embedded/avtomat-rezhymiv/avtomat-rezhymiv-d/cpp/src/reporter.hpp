#pragma once

#include <cstdint>
#include <string_view>

#include "deny.hpp"

namespace fm {

/* Сигнали зумера: пілот у полі чує їх швидше, ніж читає екран станції. */
enum class Tone : std::uint8_t {
    ModeAccepted,
    ModeRejected,
    ThrottleLock,
    Failsafe,
    Disarm
};

/* Вихідний канал автомата. Автомат нічого не знає ні про UART, ні про буфери
   телеметрії — він знає лише цей інтерфейс, а підставляє реалізацію носій:
   прошивка, стенд або тест. */
class Reporter {
public:
    Reporter() = default;
    Reporter(const Reporter&) = delete;
    Reporter& operator=(const Reporter&) = delete;
    Reporter(Reporter&&) = delete;
    Reporter& operator=(Reporter&&) = delete;
    virtual ~Reporter() = default;

    virtual void commandAck(std::uint16_t command, MavResult result) = 0;
    virtual void statusText(Severity severity, std::string_view text) = 0;
    virtual void tone(Tone tone) = 0;
};

/* Мовчазний приймач: автомат працює й без телеметрії, і це має бути видно
   в типах, а не в перевірках на нульовий вказівник у кожному виклику. */
class NullReporter final : public Reporter {
public:
    void commandAck(std::uint16_t, MavResult) override {}
    void statusText(Severity, std::string_view) override {}
    void tone(Tone) override {}
};

}  // namespace fm
