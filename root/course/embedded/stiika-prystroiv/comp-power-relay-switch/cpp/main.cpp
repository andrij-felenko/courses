// Ідіоматичний C++20 драйвер комутатора живлення слота стенда
#include <cstdint>
#include <expected>
#include <chrono>
#include <thread>
#include <concepts>

enum class SlotError {
    I2cCommunicationFailure,
    ParasiticBackfeedingDetected,
    InrushOvercurrentFault,
    SustainedOvercurrentFault
};

enum class PowerState {
    Off,
    SoftStarting,
    Active,
    Faulted
};

template <typename I2cBusType>
class SlotPowerSwitch {
public:
    static constexpr std::uint16_t MaxInrushCurrentMa = 1500;
    static constexpr std::uint16_t ParasiticThresholdMv = 500;
    static constexpr std::chrono::milliseconds SoftStartDuration{20};

    explicit constexpr SlotPowerSwitch(I2cBusType& bus, std::uint8_t slotId,
                                      std::uint8_t ioAddr, std::uint8_t inaAddr) noexcept
        : i2c_(bus), slotId_(slotId), ioAddr_(ioAddr), inaAddr_(inaAddr), state_(PowerState::Off) {}

    [[nodiscard]] std::expected<void, SlotError> powerOn() noexcept {
        auto telem = readTelemetry();
        if (!telem.has_value()) {
            return std::unexpected(SlotError::I2cCommunicationFailure);
        }

        // Перевірка залишкової напруги від паразитного підживлення
        if (telem->voltageMv > ParasiticThresholdMv) {
            state_ = PowerState::Faulted;
            return std::unexpected(SlotError::ParasiticBackfeedingDetected);
        }

        state_ = PowerState::SoftStarting;
        if (!i2c_.writeReg8(ioAddr_, 0x02, static_cast<std::uint8_t>(1U << slotId_))) {
            state_ = PowerState::Faulted;
            return std::unexpected(SlotError::I2cCommunicationFailure);
        }

        std::this_thread::sleep_for(SoftStartDuration);

        auto postTelem = readTelemetry();
        if (!postTelem.has_value()) {
            emergencyCutoff();
            return std::unexpected(SlotError::I2cCommunicationFailure);
        }

        if (postTelem->currentMa > MaxInrushCurrentMa) {
            emergencyCutoff();
            return std::unexpected(SlotError::InrushOvercurrentFault);
        }

        state_ = PowerState::Active;
        return {};
    }

    void powerOff() noexcept {
        emergencyCutoff();
        state_ = PowerState::Off;
    }

    [[nodiscard]] PowerState state() const noexcept { return state_; }

    struct Telemetry {
        std::uint16_t voltageMv{0};
        std::uint16_t currentMa{0};
    };

    [[nodiscard]] std::expected<Telemetry, SlotError> readTelemetry() noexcept {
        std::uint16_t rawCurrent{0};
        std::uint16_t rawVoltage{0};

        if (!i2c_.readReg16(inaAddr_, 0x04, rawCurrent) ||
            !i2c_.readReg16(inaAddr_, 0x02, rawVoltage)) {
            return std::unexpected(SlotError::I2cCommunicationFailure);
        }

        return Telemetry{
            .voltageMv = static_cast<std::uint16_t>((rawVoltage >> 3) * 4U),
            .currentMa = static_cast<std::uint16_t>(rawCurrent / 10U)
        };
    }

private:
    void emergencyCutoff() noexcept {
        i2c_.writeReg8(ioAddr_, 0x02, 0x00);
        state_ = PowerState::Off;
    }

    I2cBusType& i2c_;
    std::uint8_t slotId_;
    std::uint8_t ioAddr_;
    std::uint8_t inaAddr_;
    PowerState state_;
};
