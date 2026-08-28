/* i2c_driver.hpp - Публічний інтерфейс PIMPL на C++20 */
#ifndef I2C_DRIVER_HPP
#define I2C_DRIVER_HPP

#include <cstdint>
#include <cstddef>
#include <span>
#include <memory>
#include <expected>

namespace driver {

enum class Status : uint8_t;
struct I2cConfig;

class I2cPort {
public:
    explicit I2cPort(uint8_t port_index, const I2cConfig& config) noexcept;
    ~I2cPort() noexcept;

    [[nodiscard]] Status init() noexcept;
    [[nodiscard]] std::expected<size_t, Status> transfer(
        uint8_t addr,
        std::span<const uint8_t> tx,
        std::span<uint8_t> rx) noexcept;

private:
    struct Impl;
    Impl* pimpl_; // Непрозорий покажчик на приватну структуру
};

} // namespace driver

#endif
