// Сеанс роботи з ATECC608: живе стільки, скільки чип не спить, і вкладає його
// спати у власному деструкторі.
#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

#include "i2c_bus.hpp"

namespace atecc {

inline constexpr std::uint8_t kDefaultAddress = 0x60;
inline constexpr std::size_t kDigestSize = 32;
inline constexpr std::size_t kSignatureSize = 64;

using Digest = std::span<const std::uint8_t, kDigestSize>;
using Signature = std::array<std::uint8_t, kSignatureSize>;

enum class Error {
    Io,          // шина не відповіла
    Crc,         // CRC16 відповіді не збіглася
    Timeout,     // чип не встиг у відведений час виконання
    Protocol,    // довжина пакета не та, що обіцяє формат
    Device,      // чип повернув статус-пакет із кодом помилки
    NotLocked,   // зони пам'яті ще не заблоковані на виробництві
    BadArgument,
};

struct LockState {
    bool configuration = false;
    bool data = false;
};

std::string_view describe(Error error) noexcept;
std::string_view describeStatus(std::uint8_t status) noexcept;

// CRC16-CCITT з поліномом 0x8005 і нульовим початковим значенням — той самий
// розрахунок, що й усередині чипа.
[[nodiscard]] std::uint16_t crc16(std::span<const std::uint8_t> data) noexcept;

class SecureElement {
public:
    explicit SecureElement(I2cBus& bus, std::uint8_t address = kDefaultAddress) noexcept
        : bus_(bus), address_(address) {}

    ~SecureElement() { sleep(); }

    SecureElement(const SecureElement&) = delete;
    SecureElement& operator=(const SecureElement&) = delete;

    // Імпульс пробудження й перевірка слова готовності 04 11 33 43.
    [[nodiscard]] std::expected<void, Error> wake();

    // Глибокий сон. Його ж робить деструктор, тож у звичайному коді руками
    // цей виклик не потрібен.
    void sleep() noexcept;

    // Підпис зовнішнього дайджеста ключем зі слота: 32 байти R, далі 32 S.
    [[nodiscard]] std::expected<Signature, Error> signDigest(std::uint8_t slot, Digest digest);

    // Доки конфігурація не заблокована, чип відхиляє команду Sign.
    [[nodiscard]] std::expected<LockState, Error> lockState();

    [[nodiscard]] std::uint8_t lastStatus() const noexcept { return status_; }

private:
    using Milliseconds = std::chrono::milliseconds;

    // Повний цикл однієї команди. Повернений span дивиться у внутрішній
    // буфер і лишається чинним до наступної команди.
    [[nodiscard]] std::expected<std::span<const std::uint8_t>, Error> transact(
        std::span<const std::uint8_t> command, Milliseconds execMin, Milliseconds execMax);

    // Читання пакета у два прийоми: спершу байт довжини, потім увесь пакет.
    [[nodiscard]] std::expected<std::span<const std::uint8_t>, Error> readPacket();

    I2cBus& bus_;
    std::uint8_t address_;
    bool awake_ = false;
    std::uint8_t status_ = 0x00;
    std::array<std::uint8_t, 67> rx_{};
};

} // namespace atecc
