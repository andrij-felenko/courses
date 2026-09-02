#pragma once

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "ew/detector.hpp"

namespace ew {

enum class RadioError : std::uint8_t {
    Busy,       // мікросхема не відпустила лінію BUSY
    SpiFailure  // обмін по SPI не відбувся
};

// Гачки плати. Обмін — повний дуплекс однією транзакцією, NSS тримає саме ця
// функція; waitBusy чекає спаду лінії BUSY трансивера.
namespace bsp {
[[nodiscard]] bool spiTransfer(std::span<const std::byte> tx, std::span<std::byte> rx) noexcept;
[[nodiscard]] bool waitBusy(std::chrono::microseconds timeout) noexcept;
[[nodiscard]] Millis now() noexcept;
} // namespace bsp

// Читач телеметрії SX1261/1262/1268. Стану не тримає: усе, що треба, лежить
// у самій мікросхемі.
class Sx126x {
public:
    // Знімає вибірку: миттєвий RSSI, SNR останнього кадру, прапорці преамбули
    // й CRC, відновлений стан підсилення. throttle_pct лишається на виклику.
    [[nodiscard]] std::expected<RfSample, RadioError> readSample() noexcept;

private:
    struct PacketStatus {
        std::int16_t rssi_pkt_dbm{0};
        std::int8_t  snr_db{0};
    };

    [[nodiscard]] std::expected<void, RadioError> command(std::span<const std::byte> tx,
                                                          std::span<std::byte> rx) noexcept;
    [[nodiscard]] std::expected<std::uint16_t, RadioError> irqStatus() noexcept;
    [[nodiscard]] std::expected<void, RadioError> clearIrq(std::uint16_t mask) noexcept;
    [[nodiscard]] std::expected<std::int16_t, RadioError> instantRssi() noexcept;
    [[nodiscard]] std::expected<PacketStatus, RadioError> packetStatus() noexcept;
    [[nodiscard]] std::expected<std::uint8_t, RadioError> readRegister(std::uint16_t addr) noexcept;
};

} // namespace ew
