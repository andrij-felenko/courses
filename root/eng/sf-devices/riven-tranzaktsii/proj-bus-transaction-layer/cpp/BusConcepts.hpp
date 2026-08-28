/**
 * @file BusConcepts.hpp
 * @brief Сучасні інтерфейси, концепти та типи результатів на C++20.
 */

#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>
#include <string_view>

namespace embedded::bus {

/**
 * @brief Строго типізовані коди помилок транзакцій шини.
 */
enum class BusError : int8_t {
    InvalidArg   = -1,
    Timeout      = -2,
    Nack         = -3,
    Arbitration  = -4,
    Busy         = -5,
    DmaFault     = -6,
    IoError      = -7
};

/**
 * @brief Прапорці конфігурації кадрування.
 */
enum class BusFlags : uint32_t {
    None         = 0x00,
    SpiReadMsb   = 0x01,
    SpiReadLsb   = 0x02,
    AutoInc      = 0x04,
    Reg16Bit     = 0x08,
    UseDummy     = 0x10
};

[[nodiscard]] constexpr BusFlags operator|(BusFlags a, BusFlags b) noexcept {
    return static_cast<BusFlags>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

[[nodiscard]] constexpr bool has_flag(BusFlags flags, BusFlags check) noexcept {
    return (static_cast<uint32_t>(flags) & static_cast<uint32_t>(check)) != 0;
}

/**
 * @brief C++20 Концепт транспорту шини для статичного поліморфізму (Compile-time).
 */
template <typename T>
concept BusTransport = requires(T bus, uint16_t reg, std::span<uint8_t> rx_buf, std::span<const uint8_t> tx_buf) {
    { bus.read_reg(reg, rx_buf) }   -> std::same_as<std::expected<void, BusError>>;
    { bus.write_reg(reg, tx_buf) }  -> std::same_as<std::expected<void, BusError>>;
};

/**
 * @brief Абстрактний інтерфейс для динамічного поліморфізму (Runtime).
 */
class IBusAdapter {
public:
    virtual ~IBusAdapter() = default;

    [[nodiscard]] virtual std::expected<void, BusError> read_reg(uint16_t reg_addr, std::span<uint8_t> rx_data) = 0;
    [[nodiscard]] virtual std::expected<void, BusError> write_reg(uint16_t reg_addr, std::span<const uint8_t> tx_data) = 0;
    
    [[nodiscard]] virtual std::expected<void, BusError> lock(uint32_t timeout_ms) {
        (void)timeout_ms;
        return {};
    }
    virtual void unlock() noexcept {}

    /**
     * @brief Зручний шаблонний метод зчитування одного байта.
     */
    [[nodiscard]] std::expected<uint8_t, BusError> read_u8(uint16_t reg_addr) {
        uint8_t val = 0;
        auto res = read_reg(reg_addr, std::span<uint8_t>(&val, 1));
        if (!res) return std::unexpected(res.error());
        return val;
    }

    /**
     * @brief Запис одного байта.
     */
    [[nodiscard]] std::expected<void, BusError> write_u8(uint16_t reg_addr, uint8_t val) {
        return write_reg(reg_addr, std::span<const uint8_t>(&val, 1));
    }

    /**
     * @brief Атомарна модифікація бітів за маскою.
     */
    [[nodiscard]] std::expected<void, BusError> modify_reg(uint16_t reg_addr, uint8_t mask, uint8_t val) {
        auto current = read_u8(reg_addr);
        if (!current) return std::unexpected(current.error());

        uint8_t new_val = (*current & ~mask) | (val & mask);
        if (new_val == *current) return {};

        return write_u8(reg_addr, new_val);
    }
};

} // namespace embedded::bus
