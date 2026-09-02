#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "spi_bus.hpp"

namespace console {

// Драйвер Semtech SX1280 у режимі FLRC. Замість -1 і errno кожна операція
// повертає std::expected: помилку неможливо мовчки не перевірити.
enum class RadioError : std::uint8_t {
    NotResponding,   // чип не відповідає або тримає шину в 0xFF
    Busy,            // лінія BUSY не опустилася
    Timeout,         // подія не настала у відведене вікно
    BadLength        // кадр не влазить у транзакцію
};

namespace irq {
inline constexpr std::uint16_t TxDone = 0x0001;
inline constexpr std::uint16_t RxDone = 0x0002;
inline constexpr std::uint16_t CrcError = 0x0040;
inline constexpr std::uint16_t RxTxTimeout = 0x4000;
inline constexpr std::uint16_t All = 0xFFFF;
}   // namespace irq

struct Reception {
    std::span<const std::byte> payload;
    int rssiDbm;
};

class Sx1280 {
public:
    explicit Sx1280(std::uint8_t payloadLength) noexcept : payloadLength_{payloadLength} {}

    [[nodiscard]] std::expected<void, RadioError> begin() noexcept;
    [[nodiscard]] std::expected<void, RadioError> transmit(std::span<const std::byte> payload) noexcept;
    [[nodiscard]] std::expected<void, RadioError> listen(std::chrono::microseconds window) noexcept;
    [[nodiscard]] std::expected<std::uint16_t, RadioError> waitIrq(
        std::uint16_t mask, std::chrono::microseconds limit) noexcept;
    [[nodiscard]] std::expected<Reception, RadioError> read() noexcept;
    [[nodiscard]] std::expected<void, RadioError> standby() noexcept;

private:
    enum class Opcode : std::uint8_t {
        GetStatus = 0xC0,
        WriteRegister = 0x18,
        WriteBuffer = 0x1A,
        ReadBuffer = 0x1B,
        SetStandby = 0x80,
        SetRx = 0x82,
        SetTx = 0x83,
        SetRfFrequency = 0x86,
        SetPacketType = 0x8A,
        SetModulationParams = 0x8B,
        SetPacketParams = 0x8C,
        SetDioIrqParams = 0x8D,
        SetTxParams = 0x8E,
        SetBufferBase = 0x8F,
        SetRegulatorMode = 0x96,
        ClearIrqStatus = 0x97,
        GetIrqStatus = 0x15,
        GetRxBufferStatus = 0x17,
        GetPacketStatus = 0x1D
    };

    void reset() noexcept;
    [[nodiscard]] std::expected<void, RadioError> exchange(std::size_t length, bool needRx) noexcept;
    [[nodiscard]] std::expected<void, RadioError> command(Opcode op,
                                                          std::span<const std::uint8_t> params) noexcept;
    [[nodiscard]] std::expected<void, RadioError> query(Opcode op, std::span<std::uint8_t> out) noexcept;
    [[nodiscard]] std::expected<void, RadioError> writeRegister(
        std::uint16_t address, std::span<const std::uint8_t> data) noexcept;
    [[nodiscard]] std::expected<std::uint16_t, RadioError> irqStatus() noexcept;
    [[nodiscard]] std::expected<void, RadioError> clearIrq(std::uint16_t mask) noexcept;

    SpiBus bus_{};
    std::uint8_t payloadLength_;
    int lastRssi_{-127};
    // Буфери DMA — члени класу, а не статика: у пульта трансивер один,
    // і час його життя тепер збігається з часом життя буферів.
    alignas(32) std::array<std::byte, 24> tx_{};
    alignas(32) std::array<std::byte, 24> rx_{};
};

}   // namespace console
