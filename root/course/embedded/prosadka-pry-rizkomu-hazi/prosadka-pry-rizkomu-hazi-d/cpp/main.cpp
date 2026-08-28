#include <iostream>
#include <iomanip>
#include <vector>
#include <string_view>
#include <algorithm>
#include <cstdint>

struct PowerProfileConfig {
    uint8_t cells{6};
    float cell_ocv{4.10f};       // В
    float r_int{0.024f};          // 24 мОм
    float r_wire{0.003f};         // 3 мОм
    float l_wire{80e-9f};         // 80 нГн
    float c_bulk{1000e-6f};       // 1000 мкФ
    float cap_esr{0.012f};        // 12 мОм
};

struct RegulatorSpec {
    float bec_target_v{5.00f};
    float bec_dropout_v{1.40f};
    float bec_uvlo_v{6.00f};
    float ldo_target_v{3.30f};
    float ldo_dropout_v{0.25f};
    float stm32_bor_thresh_v{2.70f};
};

enum class BorSupervisorState {
    NormalOperation,
    ResetTriggered
};

class PowerNetworkSimulator {
public:
    explicit PowerNetworkSimulator(const PowerProfileConfig& cfg, 
                                   const RegulatorSpec& spec)
        : config_(cfg), spec_(spec),
          v_ocv_(cfg.cells * cfg.cell_ocv),
          r_total_(cfg.r_int + cfg.r_wire),
          v_cap_(v_ocv_),
          i_wire_(0.0f) {}

    struct StepResult {
        float time_ms;
        float load_current_a;
        float bus_voltage_v;
        float bec_voltage_v;
        float mcu_voltage_v;
        BorSupervisorState bor_state;
    };

    StepResult advance(float load_current, float dt_sec, float current_time_sec) {
        // Динаміка RLC силової шини
        float v_bus_approx = v_cap_ + (i_wire_ - load_current) * config_.cap_esr;
        float di_wire = ((v_ocv_ - v_bus_approx - i_wire_ * r_total_) / config_.l_wire) * dt_sec;
        i_wire_ = std::max(0.0f, i_wire_ + di_wire);

        float i_cap = i_wire_ - load_current;
        v_cap_ += (i_cap / config_.c_bulk) * dt_sec;
        float v_bus = v_cap_ + i_cap * config_.cap_esr;

        // Поведінка імпульсного регулятора Buck BEC 5V
        float v_5v = 0.0f;
        if (v_bus >= spec_.bec_uvlo_v) {
            v_5v = (v_bus < spec_.bec_target_v + spec_.bec_dropout_v) 
                   ? (v_bus - spec_.bec_dropout_v) 
                   : spec_.bec_target_v;
        }

        // Поведінка лінійного LDO 3.3V
        float v_3v3 = (v_5v < spec_.ldo_target_v + spec_.ldo_dropout_v)
                      ? std::max(0.0f, v_5v - spec_.ldo_dropout_v)
                      : spec_.ldo_target_v;

        // Апаратний стан супервізора BOR
        auto state = (v_3v3 < spec_.stm32_bor_thresh_v) 
                     ? BorSupervisorState::ResetTriggered 
                     : BorSupervisorState::NormalOperation;

        return StepResult{
            .time_ms = current_time_sec * 1000.0f,
            .load_current_a = load_current,
            .bus_voltage_v = v_bus,
            .bec_voltage_v = v_5v,
            .mcu_voltage_v = v_3v3,
            .bor_state = state
        };
    }

private:
    PowerProfileConfig config_;
    RegulatorSpec spec_;
    float v_ocv_;
    float r_total_;
    float v_cap_;
    float i_wire_;
};

int main() {
    PowerProfileConfig cfg;
    RegulatorSpec spec;
    PowerNetworkSimulator simulator(cfg, spec);

    constexpr float dt = 0.00001f;      // 10 мкс крок
    constexpr float t_end = 0.050f;     // 50 мс симуляції

    std::cout << "=== Симулятор перехідних процесів бортової мережі (C++20) ===\n";
    std::cout << "Конфігурація: 6S LiPo, 1000 мкФ Low-ESR, поріг BOR = 2.70 В\n\n";
    std::cout << std::left << std::setw(9)  << "Час(мс)" 
              << std::setw(11) << "Струм(А)" 
              << std::setw(11) << "V_bat(В)" 
              << std::setw(9)  << "BEC(В)" 
              << std::setw(9)  << "MCU(В)" 
              << "Стан супервізора BOR\n";
    std::cout << std::string(60, '-') << "\n";

    bool was_reset = false;
    float min_battery_v = cfg.cells * cfg.cell_ocv;

    for (float t = 0.0f; t <= t_end; t += dt) {
        float i_load = 15.0f;
        if (t >= 0.005f && t < 0.008f) {
            float ramp = (t - 0.005f) / 0.003f;
            i_load = 15.0f + ramp * (180.0f - 15.0f);
        } else if (t >= 0.008f && t < 0.030f) {
            i_load = 180.0f;
        } else if (t >= 0.030f) {
            i_load = 60.0f;
        }

        auto res = simulator.advance(i_load, dt, t);
        min_battery_v = std::min(min_battery_v, res.bus_voltage_v);

        if (res.bor_state == BorSupervisorState::ResetTriggered) {
            was_reset = true;
        }

        auto step_idx = static_cast<int>(t / dt);
        if (step_idx % 500 == 0) {
            std::cout << std::fixed << std::setprecision(2)
                      << std::setw(9)  << res.time_ms
                      << std::setw(11) << res.load_current_a
                      << std::setw(11) << res.bus_voltage_v
                      << std::setw(9)  << res.bec_voltage_v
                      << std::setw(9)  << res.mcu_voltage_v
                      << (res.bor_state == BorSupervisorState::ResetTriggered 
                          ? "RESET (Brown-out!)" 
                          : "OK (Норма)") << "\n";
        }
    }

    std::cout << std::string(60, '-') << "\n";
    std::cout << "Аналіз: Мінімальна напруга: " << min_battery_v << " В. "
              << "Підсумок: " << (was_reset ? "АВАРІЯ (BOR RESET)" : "БЕЗПЕЧНО") << "\n";

    return 0;
}
