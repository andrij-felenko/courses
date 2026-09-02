#pragma once

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <span>

/* Контракт плати: усе, чого автомат з'єднання потребує від заліза.
   Реалізацію дає файл підтримки конкретної плати. */
class ModemHal {
public:
    using Clock = std::chrono::steady_clock;

    virtual ~ModemHal() = default;

    [[nodiscard]] virtual Clock::time_point now() const = 0;

    virtual void powerSet(bool on) = 0;       /* силовий ключ VBAT_EN */
    virtual void pwrkeySet(bool pressed) = 0; /* тривалість імпульсу веде автомат */
    virtual void resetSet(bool asserted) = 0;
    [[nodiscard]] virtual bool statusPin() const = 0;

    virtual void uartWrite(std::span<const std::byte> data) = 0;
    virtual void rtsSet(bool ready) = 0; /* апаратний контроль потоку */

    [[nodiscard]] virtual std::uint16_t vbatMv() const = 0;
    [[nodiscard]] virtual std::uint32_t random() = 0;
    virtual void kickWatchdog() = 0;

    /* Пам'ять, що переживає знеструмлення (RTC Backup SRAM, EEPROM). */
    virtual bool nvRead(std::span<std::byte> dst) = 0;
    virtual bool nvWrite(std::span<const std::byte> src) = 0;
};

/* Єдиний екземпляр плати; визначає файл підтримки заліза. */
ModemHal& boardModemHal();
