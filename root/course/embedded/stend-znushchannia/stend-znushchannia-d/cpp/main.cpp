#include <cstdint>
#include <chrono>
#include <span>
#include <expected>

namespace bench {

enum class Status : uint8_t {
    Ok = 0,
    InvalidParam,
    HardwareFault,
    Timeout
};

struct StressConfig {
    uint16_t voltage_mv{3300};           // Напруга живлення (1800..5500 мВ)
    std::chrono::microseconds dropout{100}; // Тривалість провалу живлення
    bool spark_relay_en{false};          // Активація генератора іскор
    bool active_pull_down{true};         // Примусовий розряд шини N-MOSFET
};

struct Telemetry {
    uint16_t measured_mv{0};
    uint16_t current_ma{0};
    bool dut_heartbeat_ok{false};
    bool reset_triggered{false};
};

// Абстракція апаратного драйвера стенду за патерном RAII
class TortureBenchRig {
public:
    TortureBenchRig() = default;
    ~TortureBenchRig() {
        shutdown_safe();
    }

    TortureBenchRig(const TortureBenchRig&) = delete;
    TortureBenchRig& operator=(const TortureBenchRig&) = delete;

    std::expected<void, Status> init() noexcept {
        set_dac_voltage(3300);
        set_spark_relay(false);
        set_fast_pulldown(false);
        return {};
    }

    std::expected<Telemetry, Status> execute_stress(const StressConfig& cfg) noexcept {
        if (cfg.voltage_mv < 1000 || cfg.voltage_mv > 5500) {
            return std::unexpected(Status::InvalidParam);
        }
        if (cfg.dropout.count() <= 0 || cfg.dropout.count() > 1'000'000) {
            return std::unexpected(Status::InvalidParam);
        }

        // 1. Встановлюємо напругу марджинування
        set_dac_voltage(cfg.voltage_mv);

        // 2. Налаштовуємо таймерний глітчер
        configure_timer_pulse(static_cast<uint32_t>(cfg.dropout.count()));
        set_fast_pulldown(cfg.active_pull_down);

        // 3. Інжекція ЕМ-завад за потреби
        if (cfg.spark_relay_en) {
            set_spark_relay(true);
        }

        // 4. Апаратний імпульс розриву живлення (One-Pulse Mode)
        trigger_hardware_pulse();

        if (cfg.spark_relay_en) {
            set_spark_relay(false);
        }

        // 5. Зчитування телеметрії
        Telemetry tel{};
        read_power_telemetry(tel.measured_mv, tel.current_ma);
        tel.reset_triggered = read_reset_line();
        tel.dut_heartbeat_ok = (tel.current_ma > 5) && !tel.reset_triggered;

        return tel;
    }

    void shutdown_safe() noexcept {
        set_dac_voltage(0);
        set_spark_relay(false);
        set_fast_pulldown(false);
    }

private:
    void set_dac_voltage(uint16_t mv) noexcept;
    void configure_timer_pulse(uint32_t us) noexcept;
    void trigger_hardware_pulse() noexcept;
    void set_spark_relay(bool en) noexcept;
    void set_fast_pulldown(bool en) noexcept;
    void read_power_telemetry(uint16_t& mv, uint16_t& ma) noexcept;
    bool read_reset_line() noexcept;
};

} // namespace bench
