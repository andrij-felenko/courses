#include <cstdint>
#include <span>
#include <expected>

namespace driver {

/* Концепт апаратної шини для статичного поліморфізму */
template <typename T>
concept BusDevice = requires(T bus, uint8_t dev_addr, uint8_t reg_addr,
                             std::span<const uint8_t> tx, std::span<uint8_t> rx) {
    { bus.write_reg(dev_addr, reg_addr, tx) } -> std::same_as<Status>;
    { bus.read_reg(dev_addr, reg_addr, rx) }  -> std::same_as<Status>;
};

/* Драйвер датчика параметризований типом шини на етапі компіляції */
template <BusDevice TBus>
class Bmp280Sensor {
public:
    explicit Bmp280Sensor(TBus& bus, uint8_t dev_addr) noexcept
        : bus_(bus), dev_addr_(dev_addr) {}

    [[nodiscard]] Status init() noexcept {
        uint8_t chip_id{0};
        auto rx_span = std::span<uint8_t, 1>(&chip_id, 1);
        if (auto st = bus_.read_reg(dev_addr_, 0xD0, rx_span); st != Status::Ok) {
            return st;
        }
        return (chip_id == 0x58) ? Status::Ok : Status::BusError;
    }

private:
    TBus& bus_;
    uint8_t dev_addr_;
};

} // namespace driver
