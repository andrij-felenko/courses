#include <array>
#include <cstdint>
#include <expected>
#include <span>

namespace sensor {

struct Motion6AxisRaw {
    std::array<int16_t, 3> gyro{};
    std::array<int16_t, 3> accel{};
};

class SpiBusInterface {
public:
    virtual ~SpiBusInterface() = default;
    virtual void select() noexcept = 0;
    virtual void deselect() noexcept = 0;
    [[nodiscard]] virtual bool transfer(std::span<const uint8_t> tx, std::span<uint8_t> rx) noexcept = 0;
};

class SpiCsGuard {
public:
    explicit SpiCsGuard(SpiBusInterface& bus) noexcept : bus_(bus) {
        bus_.select();
    }
    ~SpiCsGuard() {
        bus_.deselect();
    }
    SpiCsGuard(const SpiCsGuard&) = delete;
    SpiCsGuard& operator=(const SpiCsGuard&) = delete;

private:
    SpiBusInterface& bus_;
};

class Lsm6dsoSpiDriver {
public:
    static constexpr uint8_t kReadFlag   = 0x80;
    static constexpr uint8_t kOutXLG_Reg = 0x22;

    explicit Lsm6dsoSpiDriver(SpiBusInterface& bus) noexcept : bus_(bus) {}

    [[nodiscard]] std::expected<Motion6AxisRaw, bool> read_motion() noexcept {
        constexpr size_t kPayloadLen = 12;
        constexpr size_t kTransferLen = 1 + kPayloadLen;

        std::array<uint8_t, kTransferLen> tx_buf{};
        std::array<uint8_t, kTransferLen> rx_buf{};
        tx_buf[0] = kReadFlag | kOutXLG_Reg;

        {
            SpiCsGuard cs_guard(bus_);
            if (!bus_.transfer(tx_buf, rx_buf)) {
                return std::unexpected(false);
            }
        }

        Motion6AxisRaw result{};
        const auto* payload = &rx_buf[1];

        for (size_t i = 0; i < 3; ++i) {
            const auto low  = static_cast<uint16_t>(payload[i * 2]);
            const auto high = static_cast<uint16_t>(payload[i * 2 + 1]);
            result.gyro[i] = static_cast<int16_t>(low | (high << 8));
        }

        for (size_t i = 0; i < 3; ++i) {
            const auto low  = static_cast<uint16_t>(payload[6 + i * 2]);
            const auto high = static_cast<uint16_t>(payload[6 + i * 2 + 1]);
            result.accel[i] = static_cast<int16_t>(low | (high << 8));
        }

        return result;
    }

private:
    SpiBusInterface& bus_;
};

} // namespace sensor
