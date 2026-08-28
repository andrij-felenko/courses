/* power_rig_driver.hpp / .cpp - RAII обгортка та інтерфейс керування на C++20 */
#include <iostream>
#include <string>
#include <format>
#include <expected>
#include <chrono>
#include <thread>

class PowerSupplyDriver {
public:
    enum class Error {
        ConnectionFailed,
        SafetyLimitExceeded,
        CommandRejected
    };

    PowerSupplyDriver(std::string ip_address, double ovp_volts, double ocp_amps)
        : ip_{std::move(ip_address)}, ovp_{ovp_volts}, ocp_{ocp_amps} {
        // У конструкторі вимикаємо вихід для гарантії безпеки (Fail-Safe)
        send_raw(":OUTP:STAT OFF\n");
        send_raw(std::format(":PROT:VOLT {:.2f}\n", ovp_));
        send_raw(std::format(":PROT:CURR {:.2f}\n", ocp_));
    }

    ~PowerSupplyDriver() {
        // Деструктор гарантовано знеструмлює клеми при виході з зони видимості
        send_raw(":OUTP:STAT OFF\n");
    }

    // Заборона копіювання для запобігання дублюванню сесії приладу
    PowerSupplyDriver(const PowerSupplyDriver&) = delete;
    PowerSupplyDriver& operator=(const PowerSupplyDriver&) = delete;
    PowerSupplyDriver(PowerSupplyDriver&&) noexcept = default;
    PowerSupplyDriver& operator=(PowerSupplyDriver&&) noexcept = default;

    [[nodiscard]] std::expected<void, Error> set_battery_model(double ocv_volts, double r_internal_ohms) noexcept {
        if (ocv_volts > ovp_ || ocv_volts < 0.0) {
            return std::unexpected(Error::SafetyLimitExceeded);
        }
        send_raw(std::format(":SOUR:VOLT {:.3f}\n", ocv_volts));
        send_raw(std::format(":SOUR:RES {:.4f}\n", r_internal_ohms));
        return {};
    }

    [[nodiscard]] std::expected<void, Error> enable_output(bool enable) noexcept {
        send_raw(enable ? ":OUTP:STAT ON\n" : ":OUTP:STAT OFF\n");
        output_enabled_ = enable;
        return {};
    }

private:
    void send_raw(const std::string& scpi_cmd) noexcept {
        std::cout << "[SCPI C++ RIG] " << scpi_cmd;
    }

    std::string ip_;
    double ovp_{0.0};
    double ocp_{0.0};
    bool output_enabled_{false};
};

class ElectronicLoadDriver {
public:
    explicit ElectronicLoadDriver(std::string ip_address) : ip_{std::move(ip_address)} {
        send_raw(":INP:STAT OFF\n");
    }

    ~ElectronicLoadDriver() {
        send_raw(":INP:STAT OFF\n");
    }

    void execute_step_response_test(double base_current_a, double step_current_a, 
                                   std::chrono::milliseconds pulse_duration) noexcept {
        send_raw(":MODE CC\n");
        send_raw(":TRAN:MODE PULSE\n");
        send_raw(std::format(":TRAN:ALEV {:.2f}\n", base_current_a));
        send_raw(std::format(":TRAN:BLEV {:.2f}\n", step_current_a));
        send_raw(std::format(":TRAN:BWID {:.4f}\n", pulse_duration.count() / 1000.0));
        send_raw(":TRAN:SLEW 5.0\n"); // 5 А/мкс швидкість наростання
        send_raw(":INP:STAT ON\n");
    }

private:
    void send_raw(const std::string& scpi_cmd) noexcept {
        std::cout << "[SCPI C++ LOAD] " << scpi_cmd;
    }

    std::string ip_;
};
