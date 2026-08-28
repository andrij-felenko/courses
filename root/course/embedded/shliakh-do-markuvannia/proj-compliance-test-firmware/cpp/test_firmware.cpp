// test_firmware.hpp / test_firmware.cpp — Об'єктний диспетчер тестових режимів
#include <cstdint>
#include <string_view>
#include <span>

enum class TestMode : uint8_t {
    Idle,
    CarrierWaveTx,
    ModulatedTx,
    ContinuousRx,
    DigitalStress
};

struct RadioConfig {
    uint8_t channel{19};
    int8_t power_dbm{4};
};

class ComplianceEngine {
public:
    ComplianceEngine() = default;

    void process_command(std::string_view cmd) {
        if (cmd.starts_with("STOP")) {
            stop_all();
            send_response("STATUS: IDLE\r\n");
        } else if (cmd.starts_with("TX_CW")) {
            stop_all();
            apply_radio_config();
            start_carrier_wave();
            current_mode_ = TestMode::CarrierWaveTx;
            send_response("STATUS: CW_TX_RUNNING\r\n");
        } else if (cmd.starts_with("TX_MOD")) {
            stop_all();
            apply_radio_config();
            start_modulated_stream();
            current_mode_ = TestMode::ModulatedTx;
            send_response("STATUS: MODULATED_TX_RUNNING\r\n");
        } else if (cmd.starts_with("RX_CONT")) {
            stop_all();
            apply_radio_config();
            start_receiver();
            current_mode_ = TestMode::ContinuousRx;
            send_response("STATUS: RX_RUNNING\r\n");
        } else if (cmd.starts_with("STRESS")) {
            stop_all();
            start_digital_stress();
            current_mode_ = TestMode::DigitalStress;
            send_response("STATUS: STRESS_RUNNING\r\n");
        } else {
            send_response("ERROR: UNKNOWN_CMD\r\n");
        }
    }

    void stop_all() noexcept {
        stop_radio_hardware();
        stop_digital_stress_hardware();
        current_mode_ = TestMode::Idle;
    }

    [[nodiscard]] TestMode current_mode() const noexcept { return current_mode_; }

private:
    TestMode current_mode_{TestMode::Idle};
    RadioConfig config_{};

    void apply_radio_config() noexcept;
    void start_carrier_wave() noexcept;
    void start_modulated_stream() noexcept;
    void start_receiver() noexcept;
    void stop_radio_hardware() noexcept;
    void start_digital_stress() noexcept;
    void stop_digital_stress_hardware() noexcept;
    void send_response(std::string_view msg) noexcept;
};
