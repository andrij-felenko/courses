#include <cstdint>
#include <array>
#include <string_view>
#include <span>
#include <vector>
#include <format>
#include <cmath>

namespace dft::diagnostics {

struct PowerRailSpec {
    std::string_view name;
    uint32_t adc_channel;
    float expected_voltage;
    float tolerance_percent;
};

struct PowerRailResult {
    float measured_voltage{0.0f};
    bool in_tolerance{false};
};

struct DiagnosticSummary {
    uint32_t passed_rails{0};
    uint32_t failed_rails{0};
    uint32_t detected_i2c_nodes{0};
    bool gpio_loopback_ok{false};
};

/* Апаратний інтерфейс драйвера */
class HardwareAbstraction {
public:
    virtual ~HardwareAbstraction() = default;
    [[nodiscard]] virtual uint16_t read_adc_raw(uint32_t channel) const = 0;
    [[nodiscard]] virtual bool ping_i2c(uint8_t addr_7bit) const = 0;
    virtual void write_gpio(uint32_t pin_idx, bool state) const = 0;
    [[nodiscard]] virtual bool read_gpio(uint32_t pin_idx) const = 0;
    virtual void log_message(std::string_view message) const = 0;
};

class BoardDiagnosticsEngine {
public:
    explicit BoardDiagnosticsEngine(const HardwareAbstraction& hal) : m_hal(hal) {}

    static constexpr std::array<PowerRailSpec, 4> POWER_SPECS {{
        { "+3.3V_SYS",  0, 3.30f, 5.0f },
        { "+1.8V_CORE", 1, 1.80f, 4.0f },
        { "+3.3V_VDDA", 2, 3.30f, 2.5f },
        { "+12V_INPUT", 3, 12.00f, 10.0f }
    }};

    [[nodiscard]] DiagnosticSummary execute_full_suite(uint32_t loopback_out, uint32_t loopback_in) const {
        DiagnosticSummary summary;
        
        m_hal.log_message("\r\n=== ПОЧАТОК АВТОМАТИЗОВАНОГО ТЕСТУВАННЯ ПЛАТИ (DFT) ===\r\n");
        audit_power_rails(summary);
        summary.detected_i2c_nodes = scan_i2c_bus();
        summary.gpio_loopback_ok = verify_gpio_loopback(loopback_out, loopback_in);
        
        print_final_report(summary);
        return summary;
    }

private:
    const HardwareAbstraction& m_hal;

    [[nodiscard]] float convert_adc_to_volts(uint32_t channel, uint16_t raw_adc) const noexcept {
        constexpr float V_REF = 3.30f;
        constexpr float ADC_MAX = 4095.0f;
        const float v_pin = (static_cast<float>(raw_adc) / ADC_MAX) * V_REF;

        if (channel == 3) {
            return v_pin * ((100.0f + 20.0f) / 20.0f); // Дільник 12V
        }
        return v_pin;
    }

    void audit_power_rails(DiagnosticSummary& summary) const {
        m_hal.log_message("\r\n=== [1] АУДИТ ШИН ЖИВЛЕННЯ ТА ТЕСТОВИХ ТОЧОК ===\r\n");

        for (const auto& spec : POWER_SPECS) {
            const uint16_t raw = m_hal.read_adc_raw(spec.adc_channel);
            const float v_meas = convert_adc_to_volts(spec.adc_channel, raw);
            const float delta = std::abs(v_meas - spec.expected_voltage);
            const float max_delta = spec.expected_voltage * (spec.tolerance_percent / 100.0f);

            if (delta <= max_delta) {
                summary.passed_rails++;
                m_hal.log_message(std::format("  [PASS] {:<11} : {:.3f} В (Очік: {:.2f} В +-{}%)\r\n",
                                              spec.name, v_meas, spec.expected_voltage, spec.tolerance_percent));
            } else {
                summary.failed_rails++;
                m_hal.log_message(std::format("  [FAIL] {:<11} : {:.3f} В (ПОХИБКА! Очік: {:.2f} В)\r\n",
                                              spec.name, v_meas, spec.expected_voltage));
            }
        }
    }

    [[nodiscard]] uint32_t scan_i2c_bus() const {
        m_hal.log_message("\r\n=== [2] СКАheaderНУВАННЯ ШИНИ I2C (0x08 - 0x77) ===\r\n");
        uint32_t found_count = 0;

        for (uint8_t addr = 0x08; addr <= 0x77; ++addr) {
            if (m_hal.ping_i2c(addr)) {
                found_count++;
                m_hal.log_message(std::format("  [FOUND] Сенсор I2C за адресою: 0x{:02X} (ACK)\r\n", addr));
            }
        }
        if (found_count == 0) {
            m_hal.log_message("  [WARN] Жодного пристрою I2C не виявлено!\r\n");
        }
        return found_count;
    }

    [[nodiscard]] bool verify_gpio_loopback(uint32_t out_pin, uint32_t in_pin) const {
        m_hal.log_message("\r\n=== [3] ТЕСТ ЦІЛІСНОСТІ ЛІНІЙ GPIO (LOOPBACK) ===\r\n");

        m_hal.write_gpio(out_pin, false);
        if (m_hal.read_gpio(in_pin) != false) {
            m_hal.log_message("  [FAIL] Лінія замкнена на VCC або порушено підтяжку!\r\n");
            return false;
        }

        m_hal.write_gpio(out_pin, true);
        if (m_hal.read_gpio(in_pin) != true) {
            m_hal.log_message("  [FAIL] Лінія замкнена на GND або виявлено обрив!\r\n");
            return false;
        }

        m_hal.log_message("  [PASS] Лінії GPIO успішно пройшли динамічний тест.\r\n");
        return true;
    }

    void print_final_report(const DiagnosticSummary& summary) const {
        m_hal.log_message(std::format("\r\n=== ПІДСУМОК САМОДІАГНОСТИКИ: Успішно шин: {}, Помилок: {}, I2C вузлів: {}, Loopback: {} ===\r\n",
                                      summary.passed_rails, summary.failed_rails, summary.detected_i2c_nodes,
                                      summary.gpio_loopback_ok ? "OK" : "FAILED"));
    }
};

} // namespace dft::diagnostics
