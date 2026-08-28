#include <cstdint>
#include <concepts>
#include <expected>
#include <span>
#include <cmath>

namespace sensors {

enum class PowerMonitorError {
    DeviceNotFound,
    BusError,
    InvalidParameter,
    CalibrationFailed
};

struct PowerReadings {
    uint32_t bus_voltage_mv{0};
    int32_t current_ma{0};
    uint32_t power_mw{0};
    int32_t shunt_voltage_uv{0};
};

template <typename I2cBus>
concept I2cMaster = requires(I2cBus& bus, uint8_t addr, uint8_t reg, std::span<const uint8_t> out_buf, std::span<uint8_t> in_buf) {
    { bus.write(addr, reg, out_buf) } -> std::same_as<bool>;
    { bus.read(addr, reg, in_buf) }   -> std::same_as<bool>;
};

template <I2cMaster Bus>
class Ina226PowerMonitor {
public:
    static constexpr uint8_t DefaultAddress = 0x40;
    static constexpr uint16_t ManufacturerIdExpected = 0x5449;

    enum class Averaging : uint16_t {
        Avg1    = (0x00 << 9),
        Avg4    = (0x01 << 9),
        Avg16   = (0x02 << 9),
        Avg64   = (0x03 << 9),
        Avg128  = (0x04 << 9),
        Avg1024 = (0x07 << 9)
    };

    enum class OperatingMode : uint16_t {
        PowerDown  = 0x00,
        Triggered  = 0x03,
        Continuous = 0x07
    };

    explicit Ina226PowerMonitor(Bus& i2c_bus, uint8_t address = DefaultAddress)
        : bus_{i2c_bus}, address_{address} {}

    std::expected<void, PowerMonitorError> initialize(double shunt_resistance_ohms,
                                                     double max_expected_current_amps,
                                                     Averaging averaging = Averaging::Avg16,
                                                     OperatingMode mode = OperatingMode::Continuous) {
        if (shunt_resistance_ohms <= 0.0 || max_expected_current_amps <= 0.0) {
            return std::unexpected(PowerMonitorError::InvalidParameter);
        }

        // Перевірка Manufacture ID
        auto manuf_id = readRegister(Register::ManufId);
        if (!manuf_id || *manuf_id != ManufacturerIdExpected) {
            return std::unexpected(PowerMonitorError::DeviceNotFound);
        }

        // Скидання мікросхеми
        if (!writeRegister(Register::Config, 0x8000)) {
            return std::unexpected(PowerMonitorError::BusError);
        }

        // Розрахунок LSB струму та калібрувального значення
        current_lsb_a_ = max_expected_current_amps / 32768.0;
        power_lsb_w_   = 25.0 * current_lsb_a_;

        double cal_val = 0.00512 / (current_lsb_a_ * shunt_resistance_ohms);
        if (cal_val > 65535.0 || cal_val < 1.0) {
            return std::unexpected(PowerMonitorError::CalibrationFailed);
        }
        calibration_reg_ = static_cast<uint16_t>(cal_val);

        if (!writeRegister(Register::Calibration, calibration_reg_)) {
            return std::unexpected(PowerMonitorError::BusError);
        }

        // Налаштування режиму вимірювання (час конверсії 1.1 мс)
        constexpr uint16_t VbusCt1100us = (0x04 << 6);
        constexpr uint16_t VshCt1100us  = (0x04 << 3);

        uint16_t config = static_cast<uint16_t>(averaging) | VbusCt1100us | VshCt1100us | static_cast<uint16_t>(mode);
        if (!writeRegister(Register::Config, config)) {
            return std::unexpected(PowerMonitorError::BusError);
        }

        return {};
    }

    std::expected<PowerReadings, PowerMonitorError> readAll() {
        PowerReadings readings;

        // Зчитування напруги шини (LSB = 1.25 мВ)
        auto vbus_raw = readRegister(Register::BusVoltage);
        if (!vbus_raw) return std::unexpected(vbus_raw.error());
        readings.bus_voltage_mv = static_cast<uint32_t>((*vbus_raw * 1250ULL) / 1000ULL);

        // Зчитування напруги шунта (LSB = 2.5 мкВ)
        auto vsh_raw = readRegister(Register::ShuntVoltage);
        if (!vsh_raw) return std::unexpected(vsh_raw.error());
        readings.shunt_voltage_uv = static_cast<int32_t>(static_cast<int16_t>(*vsh_raw) * 2.5);

        // Зчитування струму
        auto curr_raw = readRegister(Register::Current);
        if (!curr_raw) return std::unexpected(curr_raw.error());
        readings.current_ma = static_cast<int32_t>(static_cast<int16_t>(*curr_raw) * current_lsb_a_ * 1000.0);

        // Зчитування потужності
        auto pwr_raw = readRegister(Register::Power);
        if (!pwr_raw) return std::unexpected(pwr_raw.error());
        readings.power_mw = static_cast<uint32_t>(*pwr_raw * power_lsb_w_ * 1000.0);

        return readings;
    }

    std::expected<void, PowerMonitorError> setOvercurrentThreshold(double shunt_resistance_ohms, double limit_amps) {
        double v_shunt_limit_v = limit_amps * shunt_resistance_ohms;
        int16_t limit_raw = static_cast<int16_t>(v_shunt_limit_v / 0.0000025);

        if (!writeRegister(Register::AlertLimit, static_cast<uint16_t>(limit_raw))) {
            return std::unexpected(PowerMonitorError::BusError);
        }
        constexpr uint16_t ShuntOverLimitMask = (1 << 15);
        if (!writeRegister(Register::MaskEnable, ShuntOverLimitMask)) {
            return std::unexpected(PowerMonitorError::BusError);
        }
        return {};
    }

private:
    enum class Register : uint8_t {
        Config       = 0x00,
        ShuntVoltage = 0x01,
        BusVoltage   = 0x02,
        Power        = 0x03,
        Current      = 0x04,
        Calibration  = 0x05,
        MaskEnable   = 0x06,
        AlertLimit   = 0x07,
        ManufId      = 0xFE,
        DieId        = 0xFF
    };

    Bus& bus_;
    uint8_t address_;
    double current_lsb_a_{0.001};
    double power_lsb_w_{0.025};
    uint16_t calibration_reg_{0};

    std::expected<uint16_t, PowerMonitorError> readRegister(Register reg) {
        uint8_t buffer[2]{0, 0};
        if (!bus_.read(address_, static_cast<uint8_t>(reg), buffer)) {
            return std::unexpected(PowerMonitorError::BusError);
        }
        return static_cast<uint16_t>((buffer[0] << 8) | buffer[1]);
    }

    bool writeRegister(Register reg, uint16_t value) {
        const uint8_t buffer[2]{
            static_cast<uint8_t>(value >> 8),
            static_cast<uint8_t>(value & 0xFF)
        };
        return bus_.write(address_, static_cast<uint8_t>(reg), buffer);
    }
};

} // namespace sensors
