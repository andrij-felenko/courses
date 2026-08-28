#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <string_view>

enum class TestMode {
    ColdCrank,
    LoadDump,
    ReversePolarity
};

enum class ProtectionState {
    Normal,
    ReverseBlock,
    Clamping,
    Tripped
};

struct SimulationConfig {
    float dt{0.0005f};                  // 500 мкс
    float v_clamp{28.0f};               // 28 В
    float v_tmr_max{1.25f};             // 1.25 В
    float i_tmr_charge{10e-6f};         // 10 мкА
    float c_tmr{2.2e-6f};               // 2.2 мкФ
    float rds_on{0.008f};               // 8 мОм
    float i_load{4.0f};                 // 4 А
    float t_amb{25.0f};                 // 25 °C
    float rth_jc{0.5f};                 // 0.5 °C/Вт
    float thermal_tau{0.08f};           // 80 мс
};

class SurgeProtectionEmulator {
public:
    explicit SurgeProtectionEmulator(SimulationConfig cfg = {})
        : cfg_{cfg}, temp_j_{cfg.t_amb} {}

    [[nodiscard]] static float generateInputVoltage(TestMode mode, float t) noexcept {
        switch (mode) {
        case TestMode::ReversePolarity:
            return -14.4f;
        case TestMode::LoadDump:
            if (t < 0.02f) return 14.4f;
            return 14.4f + (100.0f - 14.4f) * std::exp(-(t - 0.02f) / 0.120f);
        case TestMode::ColdCrank:
            if (t < 0.02f) return 12.0f;
            if (t < 0.035f) return 3.2f;
            if (t < 0.400f) {
                const float t_crank = t - 0.035f;
                const float v_base = 6.0f + 2.0f * (t_crank / 0.365f);
                return v_base + 1.0f * std::sin(2.0f * std::numbers::pi_v<float> * 15.0f * t_crank);
            }
            if (t < 0.500f) {
                const float p = (t - 0.400f) / 0.100f;
                return 8.0f + (14.4f - 8.0f) * p;
            }
            return 14.4f;
        }
        return 14.4f;
    }

    void step(float v_in) noexcept {
        if (v_in < 0.0f) {
            state_ = ProtectionState::ReverseBlock;
            v_out_ = 0.0f;
            v_ds_ = -v_in;
            p_fet_ = 0.0f;
            v_tmr_ = 0.0f;
            return;
        }

        if (state_ == ProtectionState::Tripped) {
            v_out_ = 0.0f;
            v_ds_ = v_in;
            p_fet_ = 0.0f;
            return;
        }

        if (v_in <= cfg_.v_clamp) {
            state_ = ProtectionState::Normal;
            v_ds_ = cfg_.i_load * cfg_.rds_on;
            v_out_ = v_in - v_ds_;
            p_fet_ = v_ds_ * cfg_.i_load;
            if (v_tmr_ > 0.0f) {
                v_tmr_ -= (cfg_.i_tmr_charge * cfg_.dt / cfg_.c_tmr) * 0.5f;
                if (v_tmr_ < 0.0f) v_tmr_ = 0.0f;
            }
        } else {
            state_ = ProtectionState::Clamping;
            v_out_ = cfg_.v_clamp;
            v_ds_ = v_in - cfg_.v_clamp;
            p_fet_ = v_ds_ * cfg_.i_load;

            const float i_charge = cfg_.i_tmr_charge * (1.0f + v_ds_ / 20.0f);
            v_tmr_ += (i_charge * cfg_.dt) / cfg_.c_tmr;

            if (v_tmr_ >= cfg_.v_tmr_max) {
                state_ = ProtectionState::Tripped;
                v_out_ = 0.0f;
                p_fet_ = 0.0f;
            }
        }

        const float target_temp = cfg_.t_amb + p_fet_ * cfg_.rth_jc;
        const float alpha = cfg_.dt / (cfg_.thermal_tau + cfg_.dt);
        temp_j_ += alpha * (target_temp - temp_j_);
    }

    [[nodiscard]] ProtectionState state() const noexcept { return state_; }
    [[nodiscard]] float v_out() const noexcept { return v_out_; }
    [[nodiscard]] float v_ds() const noexcept { return v_ds_; }
    [[nodiscard]] float p_fet() const noexcept { return p_fet_; }
    [[nodiscard]] float temp_junction() const noexcept { return temp_j_; }

    [[nodiscard]] std::string_view stateName() const noexcept {
        switch (state_) {
        case ProtectionState::Normal: return "НОРМА";
        case ProtectionState::Clamping: return "ОБМЕЖЕННЯ";
        case ProtectionState::Tripped: return "ВІДСІЧЕННЯ";
        case ProtectionState::ReverseBlock: return "РЕВЕРС";
        }
        return "НЕВІДОМО";
    }

private:
    SimulationConfig cfg_;
    ProtectionState state_{ProtectionState::Normal};
    float v_out_{14.4f};
    float v_ds_{0.0f};
    float p_fet_{0.0f};
    float v_tmr_{0.0f};
    float temp_j_{25.0f};
};

int main() {
    SurgeProtectionEmulator emulator;

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "Час(мс)  Вхід(В)  Вихід(В)  V_DS(В)  P_FET(Вт)  T_крист(°C)  Стан\n";

    for (float t = 0.0f; t <= 0.350f; t += 0.025f) {
        for (float sub_t = t; sub_t < t + 0.025f; sub_t += 0.0005f) {
            const float v_in = SurgeProtectionEmulator::generateInputVoltage(TestMode::LoadDump, sub_t);
            emulator.step(v_in);
        }

        const float v_in_display = SurgeProtectionEmulator::generateInputVoltage(TestMode::LoadDump, t);
        std::cout << std::setw(6) << t * 1000.0f << "   "
                  << std::setw(6) << v_in_display << "   "
                  << std::setw(7) << emulator.v_out() << "   "
                  << std::setw(6) << emulator.v_ds() << "   "
                  << std::setw(8) << emulator.p_fet() << "   "
                  << std::setw(10) << emulator.temp_junction() << "   "
                  << emulator.stateName() << '\n';
    }
    return 0;
}
