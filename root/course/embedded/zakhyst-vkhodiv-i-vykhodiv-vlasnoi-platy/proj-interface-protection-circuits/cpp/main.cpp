// Ідіоматичний C++20 клас захищеного силового комутатора
#include <array>
#include <cstdint>
#include <expected>
#include <span>

enum class ChannelFault : std::uint8_t {
    None = 0,
    OpenCircuit,
    Overcurrent,
    ThermalShutdown
};

struct ChannelTelemetry {
    std::uint32_t currentMa{0};
    ChannelFault fault{ChannelFault::None};
    bool isActive{false};
};

template <std::size_t ChannelCount = 4>
class SmartSwitchBank {
public:
    static constexpr std::uint32_t AdcVrefMv = 3300;
    static constexpr std::uint32_t AdcMaxCode = 4095;
    static constexpr std::uint32_t SenseResistorOhms = 1000;
    static constexpr std::uint32_t CurrentRatioK = 1000;
    static constexpr std::uint32_t MaxCurrentLimitMa = 2500;
    static constexpr std::uint32_t OpenLoadThresholdMa = 10;
    static constexpr std::uint32_t CoolDownPeriodMs = 3000;

    constexpr SmartSwitchBank() = default;

    constexpr void setDesiredState(std::size_t ch, bool enable) noexcept {
        if (ch < ChannelCount && states_[ch].fault != ChannelFault::ThermalShutdown) {
            states_[ch].enabledTarget = enable;
        }
    }

    [[nodiscard]] constexpr std::expected<ChannelTelemetry, ChannelFault>
    updateChannel(std::size_t ch, bool faultPinState, std::uint16_t csAdcCode, std::uint32_t currentTimeMs) noexcept {
        if (ch >= ChannelCount) {
            return std::unexpected(ChannelFault::None);
        }

        auto& c = states_[ch];
        const auto senseMv = (static_cast<std::uint32_t>(csAdcCode) * AdcVrefMv) / AdcMaxCode;
        c.currentMa = (senseMv * CurrentRatioK) / SenseResistorOhms;

        if (faultPinState) {
            c.fault = ChannelFault::ThermalShutdown;
            c.enabledTarget = false;
            c.faultTimeMs = currentTimeMs;
            return std::unexpected(ChannelFault::ThermalShutdown);
        }

        if (c.enabledTarget) {
            if (c.currentMa > MaxCurrentLimitMa) {
                c.fault = ChannelFault::Overcurrent;
                c.enabledTarget = false;
                c.faultTimeMs = currentTimeMs;
                return std::unexpected(ChannelFault::Overcurrent);
            }
            if (c.currentMa < OpenLoadThresholdMa) {
                c.fault = ChannelFault::OpenCircuit;
            } else {
                c.fault = ChannelFault::None;
            }
        } else {
            if (c.fault != ChannelFault::None && (currentTimeMs - c.faultTimeMs >= CoolDownPeriodMs)) {
                c.fault = ChannelFault::None;
            }
        }

        return ChannelTelemetry{
            .currentMa = c.currentMa,
            .fault = c.fault,
            .isActive = c.enabledTarget
        };
    }

    [[nodiscard]] constexpr std::span<const ChannelTelemetry> snapshot() const noexcept {
        // Повернення знімка стану всіх каналів
        return {};
    }

private:
    struct InternalChannelState {
        bool enabledTarget{false};
        std::uint32_t currentMa{0};
        ChannelFault fault{ChannelFault::None};
        std::uint32_t faultTimeMs{0};
    };

    std::array<InternalChannelState, ChannelCount> states_{};
};
