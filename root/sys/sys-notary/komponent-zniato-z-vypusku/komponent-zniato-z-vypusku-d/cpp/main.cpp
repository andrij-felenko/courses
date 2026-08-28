#include <concepts>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <array>
#include <chrono>

namespace embedded::hal {

enum class AdcError : int32_t {
    CommunicationTimeout = -1,
    CalibrationFailed    = -2,
    InvalidChannel       = -3,
    UnknownHardwareRev   = -4,
    DeviceNotInitialized = -5
};

enum class ChipFamily : uint8_t {
    LegacyRevA   = 0xA1,
    SubstituteRevB = 0xB4
};

struct ChannelConfig {
    uint8_t channel_id{0};
    float   reference_voltage{3.3f};
    float   gain_multiplier{1.0f};
    float   offset_volts{0.0f};
};

template <typename TransportPolicy>
concept SpiTransport = requires(TransportPolicy t, uint8_t dev_id, std::span<const uint8_t> tx, std::span<uint8_t> rx) {
    { t.transfer(dev_id, tx, rx) } -> std::same_as<std::expected<void, AdcError>>;
    { t.delay(std::chrono::microseconds{}) } -> std::same_as<void>;
};

template <SpiTransport Transport>
class UnifiedAdcDriver {
public:
    explicit constexpr UnifiedAdcDriver(uint8_t dev_id, Transport transport)
        : dev_id_{dev_id}, transport_{std::move(transport)} {}

    [[nodiscard]] std::expected<void, AdcError> initialize() noexcept {
        const std::array<uint8_t, 2> tx_cmd{0x80, 0x00};
        std::array<uint8_t, 2> rx_buf{0, 0};

        auto res = transport_.transfer(dev_id_, tx_cmd, rx_buf);
        if (!res) return std::unexpected(res.error());

        const uint8_t silicon_id = rx_buf[1];
        if (silicon_id == static_cast<uint8_t>(ChipFamily::LegacyRevA)) {
            chip_family_ = ChipFamily::LegacyRevA;
            resolution_bits_ = 12;
            lsb_step_v_ = 3.3f / 4096.0f;
            transport_.delay(std::chrono::microseconds(250));
        } else if (silicon_id == static_cast<uint8_t>(ChipFamily::SubstituteRevB)) {
            chip_family_ = ChipFamily::SubstituteRevB;
            resolution_bits_ = 16;
            lsb_step_v_ = 3.3f / 65536.0f;

            const std::array<uint8_t, 2> cfg_cmd{0x04, 0x12};
            auto cfg_res = transport_.transfer(dev_id_, cfg_cmd, rx_buf);
            if (!cfg_res) return std::unexpected(cfg_res.error());
            transport_.delay(std::chrono::microseconds(50));
        } else {
            return std::unexpected(AdcError::UnknownHardwareRev);
        }

        is_initialized_ = true;
        return {};
    }

    [[nodiscard]] std::expected<float, AdcError> read_voltage(uint8_t channel_idx) const noexcept {
        if (!is_initialized_) return std::unexpected(AdcError::DeviceNotInitialized);
        if (channel_idx >= channels_.size()) return std::unexpected(AdcError::InvalidChannel);

        std::array<uint8_t, 3> tx_buf{0, 0, 0};
        std::array<uint8_t, 3> rx_buf{0, 0, 0};
        uint32_t raw_code = 0;

        if (chip_family_ == ChipFamily::LegacyRevA) {
            tx_buf[0] = static_cast<uint8_t>(0x10 | (channel_idx & 0x07));
            auto res = transport_.transfer(dev_id_, tx_buf, rx_buf);
            if (!res) return std::unexpected(res.error());
            raw_code = (static_cast<uint32_t>(rx_buf[1] & 0x0F) << 8) | rx_buf[2];
        } else {
            tx_buf[0] = static_cast<uint8_t>(0x30 | (channel_idx & 0x07));
            auto res = transport_.transfer(dev_id_, tx_buf, rx_buf);
            if (!res) return std::unexpected(res.error());
            raw_code = (static_cast<uint32_t>(rx_buf[1]) << 8) | rx_buf[2];
        }

        const float raw_v = static_cast<float>(raw_code) * lsb_step_v_;
        const auto& cfg = channels_[channel_idx];
        return (raw_v * cfg.gain_multiplier) + cfg.offset_volts;
    }

    constexpr void configure_channel(size_t idx, ChannelConfig cfg) noexcept {
        if (idx < channels_.size()) {
            channels_[idx] = cfg;
        }
    }

private:
    uint8_t dev_id_{0};
    Transport transport_;
    ChipFamily chip_family_{ChipFamily::LegacyRevA};
    uint8_t resolution_bits_{12};
    float lsb_step_v_{0.0f};
    bool is_initialized_{false};
    std::array<ChannelConfig, 8> channels_{};
};

} // namespace embedded::hal
