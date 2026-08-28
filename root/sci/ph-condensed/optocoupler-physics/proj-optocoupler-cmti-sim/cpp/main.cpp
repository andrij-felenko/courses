#include <iostream>
#include <vector>
#include <iomanip>
#include <memory>
#include <string_view>

struct CmtiPoint {
    double time_ns{0.0};
    double v_iso_volts{0.0};
    double dv_dt_v_per_us{0.0};
    double i_disp_ma{0.0};
    bool unshielded_trigger{false};
    bool shielded_trigger{false};
};

class CmtiSimulator {
public:
    explicit CmtiSimulator(double c_iso_pf, double threshold_ma = 2.0)
        : c_iso_farads_(c_iso_pf * 1.0e-12), threshold_ma_(threshold_ma) {}

    [[nodiscard]] std::vector<CmtiPoint> run_simulation(double v_step_volts, double rise_time_ns, size_t points = 1000) const {
        std::vector<CmtiPoint> results;
        results.reserve(points);

        constexpr double dt_sec = 1.0e-9;

        for (size_t i = 0; i < points; ++i) {
            double t = static_cast<double>(i) * dt_sec * 1.0e9;
            double v_iso = 0.0;
            double dv_dt = 0.0;

            if (t >= 10.0 && t <= (10.0 + rise_time_ns)) {
                double progress = (t - 10.0) / rise_time_ns;
                v_iso = v_step_volts * progress;
                dv_dt = (v_step_volts / (rise_time_ns * 1.0e-9)) / 1.0e6;
            } else if (t > (10.0 + rise_time_ns)) {
                v_iso = v_step_volts;
                dv_dt = 0.0;
            }

            double i_disp = (c_iso_farads_ * (dv_dt * 1.0e6)) * 1000.0;
            double i_shielded_residual = i_disp * 0.005;

            results.push_back(CmtiPoint{
                .time_ns = t,
                .v_iso_volts = v_iso,
                .dv_dt_v_per_us = dv_dt,
                .i_disp_ma = i_disp,
                .unshielded_trigger = (i_disp > threshold_ma_),
                .shielded_trigger = (i_shielded_residual > threshold_ma_)
            });
        }

        return results;
    }

private:
    double c_iso_farads_;
    double threshold_ma_;
};

int main() {
    CmtiSimulator simulator(0.6, 2.0); // C_iso = 0.6 pF, поріг 2.0 мА
    auto results = simulator.run_simulation(600.0, 15.0);

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "Час(нс) | V_iso(В) | dV/dt(кВ/мкс) | I_disp(мА) | Без екрана | З екраном\n";
    std::cout << "-----------------------------------------------------------------------\n";

    for (size_t i = 8; i <= 28; i += 2) {
        const auto& p = results[i];
        std::cout << std::setw(7) << p.time_ns << " | "
                  << std::setw(8) << p.v_iso_volts << " | "
                  << std::setw(13) << p.dv_dt_v_per_us << " | "
                  << std::setw(10) << std::setprecision(2) << p.i_disp_ma << " | "
                  << std::setw(10) << (p.unshielded_trigger ? "ПОМИЛКА!" : "ОК") << " | "
                  << std::setw(9) << (p.shielded_trigger ? "ПОМИЛКА!" : "ОК") << "\n";
    }

    return 0;
}
