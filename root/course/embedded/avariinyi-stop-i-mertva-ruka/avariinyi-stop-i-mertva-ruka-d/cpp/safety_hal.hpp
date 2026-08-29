#pragma once

// Контракт заліза для контролера безпеки: два тестові виходи, два входи
// E-Stop, петля EDM з дзеркальних NC-контактів, котушки контакторів,
// контакти 3-позиційної кнопки дозволу та засоби сигналізації.

#include <chrono>
#include <cstdint>

namespace safety {

using Millis = std::chrono::milliseconds;
using Micros = std::chrono::microseconds;

enum class Channel : std::uint8_t { A = 0, B = 1 };

constexpr Channel other(Channel ch) noexcept
{
    return ch == Channel::A ? Channel::B : Channel::A;
}

constexpr std::size_t index(Channel ch) noexcept
{
    return static_cast<std::size_t>(ch);
}

// Контакти 3-позиційної кнопки: два NO-кола дозволу, замкнені лише в
// Позиції 2, і NC-контакт паніки, що розмикається в Позиції 3.
struct EnablingContacts {
    bool circuitA{};
    bool circuitB{};
    bool panicClosed{};
};

class Hal {
public:
    virtual ~Hal() = default;

    virtual void setTestOutput(Channel ch, bool high) = 0;
    virtual bool readEstopInput(Channel ch) const = 0;

    // true — обидва контактори відпущені, силові NO розімкнені.
    virtual bool readEdmLoop() const = 0;
    virtual void setContactors(bool energize) = 0;

    virtual EnablingContacts readEnablingContacts() const = 0;
    virtual bool readResetButton() const = 0;
    virtual bool readAckButton() const = 0;
    virtual bool operatorActive() const = 0;

    virtual void setLamp(bool on) = 0;
    virtual void setBuzzer(bool on) = 0;

    // Активне очікування на час тестового імпульсу: провал мусить бути
    // коротшим за час відпускання контактора, планувальник тут не годиться.
    virtual void busyWait(Micros duration) = 0;

    virtual Millis now() const = 0;
};

}  // namespace safety
