#include <iostream>
#include <iomanip>
#include <cmath>
#include <string_view>

namespace HarvesterSim {

enum class Phase {
    ColdStart,
    MainCharging,
    ActiveBurst
};

struct Config {
    double v_src{0.040};         // 40 мВ від джерела
    double r_src{2.0};           // 2.0 Ом внутрішнього опору
    double c_aux{4.7e-6};        // 4.7 мкФ пускова ємність
    double c_store{470.0e-6};    // 470 мкФ головний накопичувач
    double v_high{3.30};         // 3.30 В поріг запуску
    double v_low{2.20};          // 2.20 В поріг відсічки
    double i_burst{0.022};       // 22 мА струм навантаження
    double t_burst{0.015};       // 15 мс активний імпульс
    double i_q{45.0e-9};         // 45 нА споживання супервізора
    double leak_i0{5.0e-9};      // 5 нА базова константа витоку
    double leak_alpha{0.95};     // нахил експоненти витоку
    double eta_cold{0.25};       // ККД JFET генератора
    double eta_main{0.82};       // ККД основного boost
};

class SystemSimulator {
public:
    explicit SystemSimulator(Config config) : cfg_{config} {}

    void step(double dt) noexcept {
        time_ += dt;

        switch (phase_) {
            case Phase::ColdStart: {
                const double p_in = (cfg_.v_src * cfg_.v_src) / (4.0 * cfg_.r_src);
                const double p_aux = p_in * cfg_.eta_cold;
                const double v_sq = v_aux_ * v_aux_ + (2.0 * p_aux * dt) / cfg_.c_aux;
                v_aux_ = std::sqrt(v_sq);

                if (v_aux_ >= 1.8) {
                    phase_ = Phase::MainCharging;
                }
                break;
            }
            case Phase::MainCharging: {
                const double p_in = (cfg_.v_src * cfg_.v_src) / (4.0 * cfg_.r_src);
                const double p_ch = p_in * cfg_.eta_main;
                const double i_leak = calculate_leakage(v_store_);
                const double p_loss = (i_leak + cfg_.i_q) * v_store_;
                const double p_net = p_ch - p_loss;

                if (p_net > 0.0) {
                    const double v_sq = v_store_ * v_store_ + (2.0 * p_net * dt) / cfg_.c_store;
                    v_store_ = std::sqrt(v_sq);
                }

                if (v_store_ >= cfg_.v_high) {
                    phase_ = Phase::ActiveBurst;
                    burst_timer_ = 0.0;
                    ++burst_count_;
                }
                break;
            }
            case Phase::ActiveBurst: {
                burst_timer_ += dt;
                const double i_total = cfg_.i_burst + cfg_.i_q + calculate_leakage(v_store_);
                const double dv = (i_total * dt) / cfg_.c_store;
                v_store_ -= dv;

                if (burst_timer_ >= cfg_.t_burst || v_store_ <= cfg_.v_low) {
                    phase_ = Phase::MainCharging;
                }
                break;
            }
        }
    }

    [[nodiscard]] double time() const noexcept { return time_; }
    [[nodiscard]] double v_aux() const noexcept { return v_aux_; }
    [[nodiscard]] double v_store() const noexcept { return v_store_; }
    [[nodiscard]] Phase phase() const noexcept { return phase_; }
    [[nodiscard]] int burst_count() const noexcept { return burst_count_; }

    [[nodiscard]] std::string_view phase_name() const noexcept {
        switch (phase_) {
            case Phase::ColdStart:    return "Холодний старт";
            case Phase::MainCharging: return "Накопичення  ";
            case Phase::ActiveBurst:  return "АКТИВНИЙ СПАЛАХ";
        }
        return "Невідомо";
    }

private:
    [[nodiscard]] double calculate_leakage(double voltage) const noexcept {
        if (voltage <= 0.0) return 0.0;
        return cfg_.leak_i0 * std::exp(cfg_.leak_alpha * voltage);
    }

    Config cfg_;
    double time_{0.0};
    double v_aux_{0.0};
    double v_store_{0.0};
    double burst_timer_{0.0};
    int burst_count_{0};
    Phase phase_{Phase::ColdStart};
};

} // namespace HarvesterSim

int main() {
    HarvesterSim::Config config;
    HarvesterSim::SystemSimulator sim(config);

    constexpr double dt = 0.001;      // крок 1 мс
    constexpr double max_time = 120.0; // 2 хвилини

    std::cout << "Час (с) | Фаза         | V_aux (В) | V_store (В) | Імпульси\n";
    std::cout << "-----------------------------------------------------------\n";

    double next_print = 0.0;
    while (sim.time() <= max_time) {
        if (sim.time() >= next_print) {
            std::cout << std::fixed << std::setprecision(2)
                      << std::setw(7) << sim.time() << " | "
                      << std::setw(12) << sim.phase_name() << " | "
                      << std::setprecision(3)
                      << std::setw(9) << sim.v_aux() << " | "
                      << std::setw(11) << sim.v_store() << " | "
                      << std::setw(8) << sim.burst_count() << "\n";

            next_print += (sim.phase() == HarvesterSim::Phase::ActiveBurst) ? 0.005 : 10.0;
        }

        sim.step(dt);
    }

    std::cout << "-----------------------------------------------------------\n";
    std::cout << "Підсумок: успішно виконано " << sim.burst_count()
              << " імпульсів за " << sim.time() << " с.\n";

    return 0;
}
