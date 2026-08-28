#include <array>
#include <cstdint>
#include <expected>
#include <span>

namespace sensor {

struct RawAxes {
    int16_t x{};
    int16_t y{};
    int16_t z{};
};

enum class BusError {
    DeviceNotFound,
    ArbitrationLost,
    BusTimeout,
    NackReceived
};

class I2cBusInterface {
public:
    virtual ~I2cBusInterface() = default;
    [[nodiscard]] virtual std::expected<void, BusError> write_read(
        uint8_t dev_addr,
        std::span<const uint8_t> tx_data,
        std::span<uint8_t> rx_data) noexcept = 0;
};

class Lsm6dsoI2cDriver {
public:
    static constexpr uint8_t kOutXLA = 0x28;

    explicit Lsm6dsoI2cDriver(I2cBusInterface& bus, uint8_t address = 0x6B) noexcept
        : bus_(bus), device_addr_(address) {}

    [[nodiscard]] std::expected<RawAxes, BusError> read_accel_raw() noexcept {
        const std::array<uint8_t, 1> reg_addr{kOutXLA};
        std::array<uint8_t, 6> raw_buf{};

        auto result = bus_.write_read(device_addr_, reg_addr, raw_buf);
        if (!result) {
            return std::unexpected(result.error());
        }

        RawAxes axes{};
        axes.x = static_cast<int16_t>(static_cast<uint16_t>(raw_buf[0]) | (static_cast<uint16_t>(raw_buf[1]) << 8));
        axes.y = static_cast<int16_t>(static_cast<uint16_t>(raw_buf[2]) | (static_cast<uint16_t>(raw_buf[3]) << 8));
        axes.z = static_cast<int16_t>(static_cast<uint16_t>(raw_buf[4]) | (static_cast<uint16_t>(raw_buf[5]) << 8));

        return axes;
    }

private:
    I2cBusInterface& bus_;
    uint8_t          device_addr_;
};

} // namespace sensor
