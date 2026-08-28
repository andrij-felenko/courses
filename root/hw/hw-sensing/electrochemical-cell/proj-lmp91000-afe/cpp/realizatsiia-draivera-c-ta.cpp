#include <cstdint>
#include <cmath>
#include <concepts>
#include <expected>
#include <optional>
#include <algorithm>

namespace sensing {

enum class TIA_Gain : uint8_t {
    External = 0x00,
    Gain_2k75 = 0x04,
    Gain_3k5  = 0x08,
    Gain_7k   = 0x0C,
    Gain_14k  = 0x10,
    Gain_35k  = 0x14,
    Gain_120k = 0x18,
    Gain_350k = 0x1C
};

enum class RLoad : uint8_t {
    R_10Ohm  = 0x00,
    R_33Ohm  = 0x01,
    R_50Ohm  = 0x02,
    R_100Ohm = 0x03
};

enum class InternalZero : uint8_t {
    Zero_20Pct = 0x00,
    Zero_50Pct = 0x20,
    Zero_67Pct = 0x40,
    Bypassed   = 0x60
};

enum class BiasSign : uint8_t {
    Negative = 0x00,
    Positive = 0x10
};

enum class BiasMagnitude : uint8_t {
    Bias_0Pct  = 0x00,
    Bias_1Pct  = 0x01,
    Bias_2Pct  = 0x02,
    Bias_4Pct  = 0x03,
    Bias_6Pct  = 0x04,
    Bias_8Pct  = 0x05,
    Bias_10Pct = 0x06,
    Bias_12Pct = 0x07,
    Bias_14Pct = 0x08,
    Bias_16Pct = 0x09,
    Bias_18Pct = 0x0A,
    Bias_20Pct = 0x0B,
    Bias_22Pct = 0x0C,
    Bias_24Pct = 0x0D
};

enum class OperationMode : uint8_t {
    DeepSleep           = 0x00,
    Galvanic2Lead       = 0x01,
    Standby             = 0x02,
    Amperometric3Lead   = 0x03,
    TemperatureTiaOn    = 0x06,
    TemperatureTiaOff   = 0x07
};

enum class AfeError {
    I2cCommunicationFailure,
    DeviceNotReady,
    InvalidConfiguration,
    UnlockFailed,
    GainNotConfigured
};

struct SensorParameters {
    TIA_Gain gain{TIA_Gain::Gain_350k};
    RLoad rload{RLoad::R_10Ohm};
    InternalZero internalZero{InternalZero::Zero_50Pct};
    BiasSign biasSign{BiasSign::Negative};
    BiasMagnitude biasMag{BiasMagnitude::Bias_0Pct};
    float vrefVolts{3.3f};
    float sensitivityNaPerPpm{70.0f};
    float baselineCurrentNa{0.0f};
};

template <typename I2cBus>
requires requires(I2cBus bus, uint8_t reg, uint8_t val, uint8_t* read_buf) {
    { bus.write_register(reg, val) } -> std::same_as<bool>;
    { bus.read_register(reg, read_buf) } -> std::same_as<bool>;
}
class LMP91000 {
public:
    constexpr explicit LMP91000(I2cBus& bus, const SensorParameters& params) noexcept
        : bus_(bus), params_(params) {}

    std::expected<void, AfeError> initialize() noexcept {
        uint8_t status = 0;
        if (!bus_.read_register(RegStatus, &status)) {
            return std::unexpected(AfeError::I2cCommunicationFailure);
        }
        if ((status & 0x01) == 0) {
            return std::unexpected(AfeError::DeviceNotReady);
        }

        if (!bus_.write_register(RegLock, 0x00)) {
            return std::unexpected(AfeError::UnlockFailed);
        }

        uint8_t tiacn = static_cast<uint8_t>(params_.gain) | static_cast<uint8_t>(params_.rload);
        if (!bus_.write_register(RegTiacn, tiacn)) {
            return std::unexpected(AfeError::I2cCommunicationFailure);
        }

        uint8_t refcn = static_cast<uint8_t>(params_.internalZero) |
                        static_cast<uint8_t>(params_.biasSign) |
                        static_cast<uint8_t>(params_.biasMag);
        if (!bus_.write_register(RegRefcn, refcn)) {
            return std::unexpected(AfeError::I2cCommunicationFailure);
        }

        if (!bus_.write_register(RegLock, 0x01)) {
            return std::unexpected(AfeError::I2cCommunicationFailure);
        }

        return setMode(OperationMode::Amperometric3Lead, false);
    }

    std::expected<void, AfeError> setMode(OperationMode mode, bool shortingFet) noexcept {
        uint8_t modecn = static_cast<uint8_t>(mode);
        if (shortingFet) {
            modecn |= 0x80;
        }
        if (!bus_.write_register(RegModecn, modecn)) {
            return std::unexpected(AfeError::I2cCommunicationFailure);
        }
        return {};
    }

    [[nodiscard]] constexpr float voltageToCurrentNanoamps(float voutVolts) const noexcept {
        float rtia = rtiaOhms();
        if (rtia <= 0.0f) return 0.0f;

        float zeroVoltage = params_.vrefVolts * zeroFraction();
        float deltaVoltage = voutVolts - zeroVoltage;

        return (deltaVoltage / rtia) * 1.0e9f;
    }

    [[nodiscard]] constexpr float calculateGasPpm(float voutVolts, float temperatureCelsius) const noexcept {
        if (params_.sensitivityNaPerPpm <= 0.0f) return 0.0f;

        float currentNa = voltageToCurrentNanoamps(voutVolts);

        float tempCorrection = 1.0f + 0.003f * (temperatureCelsius - 20.0f);
        float baselineAtTemp = params_.baselineCurrentNa * tempCorrection;

        float netCurrentNa = std::max(0.0f, currentNa - baselineAtTemp);
        float correctedSensitivity = params_.sensitivityNaPerPpm * tempCorrection;

        return netCurrentNa / correctedSensitivity;
    }

    [[nodiscard]] static constexpr float rawToTemperature(float voutVolts) noexcept {
        constexpr float V0 = 1.632f;
        constexpr float Slope = -0.0082f;
        return (voutVolts - V0) / Slope;
    }

private:
    static constexpr uint8_t RegStatus = 0x00;
    static constexpr uint8_t RegLock   = 0x01;
    static constexpr uint8_t RegTiacn  = 0x10;
    static constexpr uint8_t RegRefcn  = 0x11;
    static constexpr uint8_t RegModecn = 0x12;

    I2cBus& bus_;
    SensorParameters params_;

    [[nodiscard]] constexpr float rtiaOhms() const noexcept {
        switch (params_.gain) {
            case TIA_Gain::Gain_2k75: return 2750.0f;
            case TIA_Gain::Gain_3k5:  return 3500.0f;
            case TIA_Gain::Gain_7k:   return 7000.0f;
            case TIA_Gain::Gain_14k:  return 14000.0f;
            case TIA_Gain::Gain_35k:  return 35000.0f;
            case TIA_Gain::Gain_120k: return 120000.0f;
            case TIA_Gain::Gain_350k: return 350000.0f;
            default:                  return 0.0f;
        }
    }

    [[nodiscard]] constexpr float zeroFraction() const noexcept {
        switch (params_.internalZero) {
            case InternalZero::Zero_20Pct: return 0.20f;
            case InternalZero::Zero_50Pct: return 0.50f;
            case InternalZero::Zero_67Pct: return 0.67f;
            default:                       return 0.50f;
        }
    }
};

} // namespace sensing
