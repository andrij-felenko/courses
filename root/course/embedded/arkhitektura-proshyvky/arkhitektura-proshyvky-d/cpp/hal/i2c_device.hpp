// hal/i2c_device.hpp — мікросхема на шині як окреме поняття.
// Драйвер тримає I2cDevice, а не пару «шина + адреса»: адресу не можна
// переплутати з номером регістра, бо це різні місця в сигнатурі, і не
// можна забути, бо вона зашита в об'єкт при створенні.
//
// Клас навмисно тонкий і повністю вбудовуваний: після оптимізації від
// нього лишається той самий непрямий виклик, що й у варіанті на C.
#pragma once

#include "hal/i2c_bus.hpp"

#include <array>

namespace hal {

class I2cDevice {
public:
    constexpr I2cDevice(II2cBus& bus, std::uint8_t address) noexcept
        : bus_{&bus}, address_{address} {}

    [[nodiscard]] constexpr std::uint8_t address() const noexcept { return address_; }

    [[nodiscard]] std::expected<void, I2cError>
    read_regs(std::uint8_t reg, std::span<std::uint8_t> dst) const
    {
        if (dst.empty()) {
            return std::unexpected{I2cError::BadArgs};
        }
        const std::array<std::uint8_t, 1> tx{reg};
        return bus_->write_read(address_, tx, dst);
    }

    [[nodiscard]] std::expected<std::uint8_t, I2cError>
    read_reg(std::uint8_t reg) const
    {
        std::array<std::uint8_t, 1> rx{};
        if (auto res = read_regs(reg, rx); !res) {
            return std::unexpected{res.error()};
        }
        return rx[0];
    }

    [[nodiscard]] std::expected<void, I2cError>
    write_reg(std::uint8_t reg, std::uint8_t value) const
    {
        const std::array<std::uint8_t, 2> frame{reg, value};
        return bus_->write(address_, frame);
    }

    // Записати й перечитати: дешева перевірка того, що мікросхема справді
    // прийняла конфігурацію, а не просто підтвердила адресу.
    [[nodiscard]] std::expected<void, I2cError>
    write_reg_verify(std::uint8_t reg, std::uint8_t value) const
    {
        if (auto res = write_reg(reg, value); !res) {
            return res;
        }
        const auto readback = read_reg(reg);
        if (!readback) {
            return std::unexpected{readback.error()};
        }
        if (*readback != value) {
            return std::unexpected{I2cError::BusError};
        }
        return {};
    }

    // Чи відгукується мікросхема (запис нульової довжини).
    [[nodiscard]] std::expected<void, I2cError> probe() const
    {
        return bus_->write(address_, std::span<const std::uint8_t>{});
    }

private:
    II2cBus*     bus_;
    std::uint8_t address_;
};

} // namespace hal
