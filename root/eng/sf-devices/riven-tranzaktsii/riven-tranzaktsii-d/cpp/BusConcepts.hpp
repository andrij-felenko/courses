/**
 * @file BusConcepts.hpp
 * @brief Сучасний інтерфейс транзакцій та концепти на C++20.
 */

#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>

namespace embedded::bus {

enum class BusError : int8_t {
    InvalidParam = -1,
    Timeout      = -2,
    Nack         = -3,
    Arbitration  = -4,
    IoError      = -5
};

/**
 * @brief C++20 Концепт для статичного поліморфізму (Zero-Cost Abstraction).
 */
template <typename T>
concept BusTransport = requires(T bus, uint16_t reg, std::span<uint8_t> rx, std::span<const uint8_t> tx) {
    { bus.read_reg(reg, rx) }   -> std::same_as<std::expected<void, BusError>>;
    { bus.write_reg(reg, tx) }  -> std::same_as<std::expected<void, BusError>>;
};

/**
 * @brief Абстрактний базовий клас для динамічного поліморфізму (Runtime).
 */
class IBusAdapter {
public:
    virtual ~IBusAdapter() = default;

    [[nodiscard]] virtual std::expected<void, BusError> read_reg(uint16_t reg, std::span<uint8_t> rx) = 0;
    [[nodiscard]] virtual std::expected<void, BusError> write_reg(uint16_t reg, std::span<const uint8_t> tx) = 0;
    
    [[nodiscard]] virtual std::expected<void, BusError> lock(uint32_t timeout_ms) {
        (void)timeout_ms; return {};
    }
    virtual void unlock() noexcept {}

    [[nodiscard]] std::expected<uint8_t, BusError> read_u8(uint16_t reg) {
        uint8_t val = 0;
        auto res = read_reg(reg, std::span<uint8_t>(&val, 1));
        if (!res) return std::unexpected(res.error());
        return val;
    }

    [[nodiscard]] std::expected<void, BusError> write_u8(uint16_t reg, uint8_t val) {
        return write_reg(reg, std::span<const uint8_t>(&val, 1));
    }

    [[nodiscard]] std::expected<void, BusError> modify_reg(uint16_t reg, uint8_t clear_mask, uint8_t set_mask) {
        auto current = read_u8(reg);
        if (!current) return std::unexpected(current.error());

        uint8_t new_val = (*current & ~clear_mask) | (set_mask & clear_mask);
        if (new_val == *current) return {}; // Уникаємо зайвого запису

        return write_u8(reg, new_val);
    }
};

} // namespace embedded::bus
