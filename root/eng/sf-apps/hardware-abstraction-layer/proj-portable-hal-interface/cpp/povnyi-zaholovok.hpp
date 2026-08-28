#ifndef PORTABLE_HAL_CXX20_H
#define PORTABLE_HAL_CXX20_H

#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <system_error>

namespace hal {

/* Перелік уніфікованих статусів виконання операцій */
enum class Status : int8_t {
    Ok             =  0,
    Error          = -1,
    Timeout        = -2,
    Busy           = -3,
    Nack           = -4,
    InvalidArg     = -5,
    NotSupported   = -6
};

/* Допоміжний метод перевірки успіху */
constexpr bool is_ok(Status s) noexcept { return s == Status::Ok; }

enum class PinLevel : uint8_t {
    Low  = 0,
    High = 1
};

enum class PinMode : uint8_t {
    Input,
    OutputPushPull,
    OutputOpenDrain
};

enum class PinPull : uint8_t {
    None,
    Up,
    Down
};

struct PinConfig {
    PinMode mode{PinMode::OutputPushPull};
    PinPull pull{PinPull::None};
};

/* C++20 Концепт цифрової лінії вводу-виводу (GPIO) */
template <typename T>
concept GpioPin = requires(T pin, PinLevel lvl, const PinConfig& cfg) {
    { pin.init(cfg) } -> std::same_as<Status>;
    { pin.set_level(lvl) } -> std::same_as<Status>;
    { pin.get_level() } -> std::same_as<PinLevel>;
    { pin.toggle() } -> std::same_as<Status>;
};

/* C++20 Концепт шини I2C Master */
template <typename T>
concept I2cMaster = requires(T bus, uint8_t addr, std::span<const uint8_t> tx,
                             std::span<uint8_t> rx, uint32_t timeout_ms) {
    { bus.write(addr, tx, timeout_ms) } -> std::same_as<Status>;
    { bus.read(addr, rx, timeout_ms) } -> std::same_as<Status>;
    { bus.write_read(addr, tx, rx, timeout_ms) } -> std::same_as<Status>;
};

/* C++20 Концепт шини SPI Master */
template <typename T>
concept SpiMaster = requires(T bus, std::span<const uint8_t> tx,
                             std::span<uint8_t> rx, uint32_t timeout_ms) {
    { bus.transfer(tx, rx, timeout_ms) } -> std::same_as<Status>;
    { bus.write(tx, timeout_ms) } -> std::same_as<Status>;
    { bus.read(rx, timeout_ms) } -> std::same_as<Status>;
};

} // namespace hal

#endif /* PORTABLE_HAL_CXX20_H */
