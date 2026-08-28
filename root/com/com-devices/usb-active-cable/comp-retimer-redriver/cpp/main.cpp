#include <cstdint>
#include <concepts>
#include <optional>
#include <span>

template <typename I2cBus>
concept I2cMaster = requires(I2cBus bus, uint8_t addr, uint8_t reg, uint8_t val, uint8_t& out_val) {
    { bus.write_reg(addr, reg, val) } -> std::same_as<bool>;
    { bus.read_reg(addr, reg, out_val) } -> std::same_as<bool>;
};

template <I2cMaster Bus>
class RetimerController {
public:
    static constexpr uint8_t RegChCtrlBase  = 0x10;
    static constexpr uint8_t RegCtleConfig  = 0x14;
    static constexpr uint8_t RegTxDeemph    = 0x18;
    static constexpr uint8_t RegCdrStatus   = 0x20;
    static constexpr uint8_t CdrLockBit     = 1 << 7;

    constexpr RetimerController(Bus& bus, uint8_t i2c_addr, uint8_t channels) noexcept
        : bus_(bus), addr_(i2c_addr), channel_count_(channels) {}

    [[nodiscard]] bool configure_channel(uint8_t ch, uint8_t ctle_boost_db, uint8_t deemph_db) noexcept {
        if (ch >= channel_count_ || ctle_boost_db > 15 || deemph_db > 7) {
            return false;
        }

        const uint8_t offset = ch * 0x10;
        const uint8_t ctle_reg = RegCtleConfig + offset;
        const uint8_t tx_reg = RegTxDeemph + offset;

        if (!bus_.write_reg(addr_, ctle_reg, ctle_boost_db & 0x0F)) {
            return false;
        }
        return bus_.write_reg(addr_, tx_reg, deemph_db & 0x07);
    }

    [[nodiscard]] std::optional<bool> is_channel_locked(uint8_t ch) const noexcept {
        if (ch >= channel_count_) {
            return std::nullopt;
        }
        uint8_t status = 0;
        const uint8_t reg = RegCdrStatus + (ch * 0x10);
        if (!bus_.read_reg(addr_, reg, status)) {
            return std::nullopt;
        }
        return (status & CdrLockBit) != 0;
    }

private:
    Bus& bus_;
    uint8_t addr_;
    uint8_t channel_count_;
};
