#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <expected>

namespace driver {

enum class BusStatus : int8_t {
    Ok = 0,
    Timeout = -1,
    Nack = -2,
    IoError = -3
};

/* C++20 концепт, що гарантує сумісність транспортного рівня */
template <typename T>
concept I2cBus = requires(T bus, uint8_t dev, uint8_t reg, std::span<uint8_t> rx, std::span<const uint8_t> tx) {
    { bus.read_reg(dev, reg, rx) } -> std::same_as<BusStatus>;
    { bus.write_reg(dev, reg, tx) } -> std::same_as<BusStatus>;
    { bus.get_time_us() } -> std::same_as<uint32_t>;
};

} // namespace driver
