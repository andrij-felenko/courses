// mdio_bitbang.hpp - C++20 реалізація драйвера Bit-Banging MDC/MDIO
#pragma once

#include <cstdint>
#include <concepts>
#include <expected>
#include <optional>

namespace eth::mdio {

enum class Error : uint8_t {
    Timeout,
    NoDevice,
    BusCollision,
    InvalidParameter
};

// Концепт для валідації апаратних операцій GPIO на етапі компіляції
template <typename T>
concept GpioOperations = requires(T ops, bool lvl, bool is_out) {
    { ops.set_mdc(lvl) } noexcept;
    { ops.set_mdio_level(lvl) } noexcept;
    { ops.get_mdio_level() } noexcept -> std::same_as<bool>;
    { ops.set_mdio_direction(is_out) } noexcept;
    { ops.delay_half_period() } noexcept;
};

template <GpioOperations Ops>
class BitBangBus {
public:
    explicit constexpr BitBangBus(Ops ops) noexcept : ops_(ops) {}

    void init() const noexcept {
        ops_.set_mdio_direction(true);
        ops_.set_mdio_level(true);
        ops_.set_mdc(false);
        ops_.delay_half_period();
    }

    [[nodiscard]] std::expected<void, Error> write_c22(uint8_t phy_addr, uint8_t reg_addr, uint16_t data) const noexcept {
        if (phy_addr > 31 || reg_addr > 31) return std::unexpected(Error::InvalidParameter);

        send_preamble();
        ops_.set_mdio_direction(true);

        send_bits(0b01, 2);              // Start of Frame (ST = 01)
        send_bits(0b01, 2);              // Opcode Write (OP = 01)
        send_bits(phy_addr, 5);          // PHY Address
        send_bits(reg_addr, 5);          // Register Address
        send_bits(0b10, 2);              // Turnaround (TA = 10)
        send_bits(data, 16);             // Data D15..D0

        release_bus();
        return {};
    }

    [[nodiscard]] std::expected<uint16_t, Error> read_c22(uint8_t phy_addr, uint8_t reg_addr) const noexcept {
        if (phy_addr > 31 || reg_addr > 31) return std::unexpected(Error::InvalidParameter);

        send_preamble();
        ops_.set_mdio_direction(true);

        send_bits(0b01, 2);              // Start of Frame (ST = 01)
        send_bits(0b10, 2);              // Opcode Read (OP = 10)
        send_bits(phy_addr, 5);          // PHY Address
        send_bits(reg_addr, 5);          // Register Address

        // Turnaround: перехід у режим входу (Hi-Z)
        ops_.set_mdio_direction(false);
        clock_cycle();                   // Такт Z

        ops_.set_mdc(true);
        ops_.delay_half_period();
        const bool ack_bit = ops_.get_mdio_level();
        ops_.set_mdc(false);
        ops_.delay_half_period();

        if (ack_bit) {
            // Лінія залишилася на рівні 1 — жоден трансивер не відповів
            return std::unexpected(Error::NoDevice);
        }

        const uint16_t value = receive_bits(16);
        release_bus();
        return value;
    }

    [[nodiscard]] std::expected<void, Error> write_c45(uint8_t prt, uint8_t dev, uint16_t reg, uint16_t data) const noexcept {
        if (prt > 31 || dev > 31) return std::unexpected(Error::InvalidParameter);

        // Крок 1: Кадр передачі адреси (OP = 00)
        send_preamble();
        ops_.set_mdio_direction(true);
        send_bits(0b00, 2); // ST = 00 (Clause 45)
        send_bits(0b00, 2); // OP = 00 (Address)
        send_bits(prt, 5);
        send_bits(dev, 5);
        send_bits(0b10, 2); // TA = 10
        send_bits(reg, 16); // 16-бітна адреса
        release_bus();

        // Крок 2: Кадр передачі даних (OP = 01)
        send_preamble();
        ops_.set_mdio_direction(true);
        send_bits(0b00, 2); // ST = 00
        send_bits(0b01, 2); // OP = 01 (Write)
        send_bits(prt, 5);
        send_bits(dev, 5);
        send_bits(0b10, 2); // TA = 10
        send_bits(data, 16);
        release_bus();

        return {};
    }

    [[nodiscard]] std::expected<uint16_t, Error> read_c45(uint8_t prt, uint8_t dev, uint16_t reg) const noexcept {
        if (prt > 31 || dev > 31) return std::unexpected(Error::InvalidParameter);

        // Крок 1: Кадр адреси
        send_preamble();
        ops_.set_mdio_direction(true);
        send_bits(0b00, 2);
        send_bits(0b00, 2);
        send_bits(prt, 5);
        send_bits(dev, 5);
        send_bits(0b10, 2);
        send_bits(reg, 16);
        release_bus();

        // Крок 2: Кадр читання даних (OP = 11)
        send_preamble();
        ops_.set_mdio_direction(true);
        send_bits(0b00, 2);
        send_bits(0b11, 2); // OP = 11 (Read)
        send_bits(prt, 5);
        send_bits(dev, 5);

        ops_.set_mdio_direction(false);
        clock_cycle(); // Z такт

        ops_.set_mdc(true);
        ops_.delay_half_period();
        const bool ack = ops_.get_mdio_level();
        ops_.set_mdc(false);
        ops_.delay_half_period();

        if (ack) return std::unexpected(Error::NoDevice);

        const uint16_t val = receive_bits(16);
        release_bus();
        return val;
    }

    [[nodiscard]] uint32_t scan_bus() const noexcept {
        uint32_t found_mask = 0;
        for (uint8_t addr = 0; addr < 32; ++addr) {
            auto res = read_c22(addr, 0x02); // Читаємо Регістр 2 (PHYID1)
            if (res.has_value() && *res != 0xFFFFU && *res != 0x0000U) {
                found_mask |= (1U << addr);
            }
        }
        return found_mask;
    }

    [[nodiscard]] bool get_link_status(uint8_t phy_addr) const noexcept {
        // Подвійне читання для коректного скидання апаратної засувки Latching Low
        auto first_read  = read_c22(phy_addr, 0x01);
        auto second_read = read_c22(phy_addr, 0x01);
        if (!second_read.has_value()) return false;
        return (*second_read & (1U << 2)) != 0;
    }

private:
    Ops ops_;

    void clock_cycle() const noexcept {
        ops_.set_mdc(true);
        ops_.delay_half_period();
        ops_.set_mdc(false);
        ops_.delay_half_period();
    }

    void send_preamble() const noexcept {
        ops_.set_mdio_direction(true);
        ops_.set_mdio_level(true);
        for (int i = 0; i < 32; ++i) {
            clock_cycle();
        }
    }

    void send_bits(uint32_t val, uint8_t count) const noexcept {
        for (int i = count - 1; i >= 0; --i) {
            const bool bit = (val >> i) & 1U;
            ops_.set_mdio_level(bit);
            ops_.delay_half_period();
            ops_.set_mdc(true);
            ops_.delay_half_period();
            ops_.set_mdc(false);
        }
    }

    [[nodiscard]] uint16_t receive_bits(uint8_t count) const noexcept {
        uint16_t result = 0;
        for (int i = 0; i < count; ++i) {
            ops_.set_mdc(true);
            ops_.delay_half_period();
            result = static_cast<uint16_t>((result << 1) | (ops_.get_mdio_level() ? 1U : 0U));
            ops_.set_mdc(false);
            ops_.delay_half_period();
        }
        return result;
    }

    void release_bus() const noexcept {
        ops_.set_mdio_direction(false);
        clock_cycle();
    }
};

} // namespace eth::mdio
