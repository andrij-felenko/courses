// eom_driver.hpp - C++20 Wrapper та об'єктно-орієнтований інтерфейс EOM Controller
#ifndef EOM_DRIVER_HPP
#define EOM_DRIVER_HPP

#include <memory>
#include <string>
#include <vector>
#include <expected>
#include <span>
#include <chrono>

namespace eom {

enum class CrystalType { DKDP, LiNbO3, BBO, KTP, Custom };
enum class Geometry { Longitudinal, Transverse };
enum class BiasMode { Manual, QuadNull, MinTransmission, MaxTransmission };

enum class DriverError {
    InvalidParam,
    OverVoltage,
    OverTemperature,
    LockLost,
    CommunicationFailure
};

struct ModulatorConfig {
    CrystalType crystal{CrystalType::LiNbO3};
    Geometry geometry{Geometry::Transverse};
    double wavelength_nm{1550.0};
    double v_pi_nominal_v{300.0};
    double max_voltage_v{500.0};
    double max_temp_c{65.0};
};

struct Telemetry {
    double bias_voltage_v{0.0};
    double temperature_c{0.0};
    double optical_power_mw{0.0};
    double thd_percent{0.0};
    bool hv_enabled{false};
    bool bias_locked{false};
};

class EomController {
public:
    virtual ~EomController() = default;

    [[nodiscard]] virtual std::expected<void, DriverError> initialize() = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> configure(const ModulatorConfig& cfg) = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> set_hv_enable(bool enable) = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> set_bias_voltage(double volts) = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> set_bias_mode(BiasMode mode) = 0;
    [[nodiscard]] virtual std::expected<double, DriverError> auto_calibrate_v_pi() = 0;
    [[nodiscard]] virtual std::expected<Telemetry, DriverError> read_telemetry() const = 0;
    [[nodiscard]] virtual std::expected<std::vector<double>, DriverError> capture_response_curve(size_t points) = 0;

    static std::unique_ptr<EomController> create_hardware_device(std::string_view port_name, uint32_t baud_rate);
    static std::unique_ptr<EomController> create_simulator_device(const ModulatorConfig& cfg);
};

} // namespace eom

#endif // EOM_DRIVER_HPP
