#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace hal {

enum class BusStatus : int8_t {
    Ok = 0,
    ErrNack = -1,
    ErrTimeout = -2,
    ErrOverrun = -3
};

class II2cInterface {
public:
    virtual ~II2cInterface() = default;
    virtual BusStatus transfer(uint8_t dev_addr,
                               std::span<const uint8_t> tx,
                               std::span<uint8_t> rx) = 0;
};

} // namespace hal

namespace devices {

class AmbientSensor {
public:
    explicit AmbientSensor(hal::II2cInterface& bus, uint8_t dev_addr) noexcept
        : bus_(bus), dev_addr_(dev_addr), last_raw_value_(0) {}

    [[nodiscard]] std::expected<int16_t, hal::BusStatus> read_value() {
        const uint8_t reg = 0x02;
        const std::span<const uint8_t> tx{&reg, 1};
        uint8_t raw[2] = {0, 0};
        const std::span<uint8_t> rx{raw, 2};

        const hal::BusStatus status = bus_.transfer(dev_addr_, tx, rx);
        if (status != hal::BusStatus::Ok) {
            return std::unexpected(status);
        }

        const auto val = static_cast<int16_t>((raw[0] << 8) | raw[1]);
        last_raw_value_ = val;
        return val;
    }

    [[nodiscard]] int16_t last_value() const noexcept { return last_raw_value_; }

private:
    hal::II2cInterface& bus_;
    uint8_t dev_addr_;
    int16_t last_raw_value_;
};

} // namespace devices
