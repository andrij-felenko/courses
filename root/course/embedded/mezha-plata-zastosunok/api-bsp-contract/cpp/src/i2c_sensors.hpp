#pragma once

#include "bsp/platform.hpp"
#include "bsp/status.hpp"

#include <cstdint>
#include <expected>
#include <optional>

namespace bsp::detail {

/**
 * @brief Давач температури й вологості SHT3x.
 *
 * Кожне слово відповіді захищене CRC-8 (поліном 0x31): биття на лінії
 * ловиться тут, а не в застосунку.
 */
class Sht3x {
public:
    struct Reading {
        std::int16_t  temperature_centi_c{};
        std::uint16_t humidity_centi_pct{};
    };

    explicit Sht3x(IPlatform& platform, std::uint8_t address = 0x44) noexcept
        : platform_{platform}, address_{address} {}

    [[nodiscard]] std::expected<Reading, Status> measure() noexcept;

private:
    IPlatform&   platform_;
    std::uint8_t address_;
};

/**
 * @brief Барометр BMP280 у режимі forced (одне вимірювання на запит).
 *
 * Калібрувальні коефіцієнти читаються один раз і кешуються; знеструмлення
 * домену робить кеш недійсним — invalidate().
 */
class Bmp280 {
public:
    explicit Bmp280(IPlatform& platform, std::uint8_t address = 0x76) noexcept
        : platform_{platform}, address_{address} {}

    [[nodiscard]] std::expected<std::uint32_t, Status> pressure_pa() noexcept;

    void invalidate() noexcept { calibration_.reset(); }

private:
    struct Calibration {
        std::uint16_t t1{};
        std::int16_t  t2{}, t3{};
        std::uint16_t p1{};
        std::int16_t  p2{}, p3{}, p4{}, p5{}, p6{}, p7{}, p8{}, p9{};
    };

    [[nodiscard]] Result read_regs(std::uint8_t reg, std::span<std::uint8_t> out) noexcept;
    [[nodiscard]] Result write_reg(std::uint8_t reg, std::uint8_t value) noexcept;
    [[nodiscard]] std::expected<Calibration, Status> load_calibration() noexcept;
    [[nodiscard]] Result wait_ready() noexcept;

    IPlatform&                 platform_;
    std::uint8_t               address_;
    std::optional<Calibration> calibration_{};
};

} // namespace bsp::detail
