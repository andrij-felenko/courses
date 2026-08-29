// twi.hpp — апаратна шина I2C ATmega328P.
//
// Проти C-версії тут дві змістовні заміни, а не косметика: STOP видає
// деструктор Transaction (тож жодна гілка виходу не може забути віддати
// шину), а буфер читання приїжджає як std::span — довжина подорожує
// разом із вказівником і не може розійтися з ним.

#pragma once

#include <cstdint>
#include <span>

#include "result.hpp"

namespace gimbal {

enum class TwiError : std::uint8_t {
    None = 0,
    Timeout,   // Апарат не підняв TWINT за відведений час
    Nack,      // Ведений не квитував адресу чи байт
    BusState   // Стан TWI не той, якого чекали
};

// Сім бітів адреси окремим типом: у голому uint8_t легко переплутати
// адресу з номером регістра, а зсув на біт читання зробити двічі.
class DeviceAddress {
public:
    constexpr explicit DeviceAddress(std::uint8_t addr7) noexcept : addr7_{addr7} {}

    [[nodiscard]] constexpr std::uint8_t write_byte() const noexcept {
        return static_cast<std::uint8_t>(addr7_ << 1);
    }
    [[nodiscard]] constexpr std::uint8_t read_byte() const noexcept {
        return static_cast<std::uint8_t>((addr7_ << 1) | 1u);
    }

private:
    std::uint8_t addr7_;
};

class Twi {
public:
    // Один байт на 400 кГц триває ~22 мкс; 2000 мкс — це вже поламка.
    static constexpr std::uint16_t kTimeoutUs = 2000;

    void begin(std::uint32_t scl_hz = 400000UL) noexcept;

    Result<void, TwiError> write_register(DeviceAddress dev,
                                          std::uint8_t reg,
                                          std::uint8_t value) noexcept;

    Result<void, TwiError> read_registers(DeviceAddress dev,
                                          std::uint8_t reg,
                                          std::span<std::uint8_t> dst) noexcept;

    // Дев'ять імпульсів на SCL плюс ручний STOP: витягує шину з залипання
    // після наведення від колектора мотора.
    void recover_bus() noexcept;

private:
    // RAII-охорона обміну: поки об'єкт живий — шина наша, деструктор
    // безумовно віддає її STOP-ом. Саме це в C-версії робили goto fail.
    class Transaction {
    public:
        explicit Transaction(Twi& bus) noexcept : bus_{bus} {}
        ~Transaction() noexcept { bus_.stop(); }

        Transaction(const Transaction&) = delete;
        Transaction& operator=(const Transaction&) = delete;

    private:
        Twi& bus_;
    };

    Result<void, TwiError> wait_flag() noexcept;
    Result<void, TwiError> start(std::uint8_t expected_status) noexcept;
    Result<void, TwiError> write_byte(std::uint8_t data, std::uint8_t expected_status) noexcept;
    Result<std::uint8_t, TwiError> read_byte(bool ack) noexcept;
    void stop() noexcept;
};

}  // namespace gimbal
