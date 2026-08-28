#include <iostream>
#include <vector>
#include <cmath>
#include <expected>
#include <span>
#include <format>

namespace laser_sim {

constexpr double CONST_Q = 1.602176634e-19;
constexpr double CONST_HC = 1.98644586e-25;

struct DiodeConfig {
    double lambda_0_nm{808.0};
    double I_th0_mA{40.0};
    double T_0_K{140.0};
    double eta_d{0.85};
    double R_s_ohm{2.5};
    double R_th_KW{35.0};
    double dlambda_dT{0.28};
    double T_sub_C{25.0};
};

struct DataPoint {
    double current_mA;
    double voltage_V;
    double power_mW;
    double temp_C;
    double lambda_nm;
    double wpe_percent;
};

enum class SimError { InvalidStep, InvalidCurrentRange };

class LaserDiodeSimulator {
public:
    explicit LaserDiodeSimulator(DiodeConfig cfg) : config_(cfg) {}

    [[nodiscard]] std::expected<std::vector<DataPoint>, SimError> 
    run(double I_max_mA, double I_step_mA) const {
        if (I_step_mA <= 0.0) return std::unexpected(SimError::InvalidStep);
        if (I_max_mA <= 0.0) return std::unexpected(SimError::InvalidCurrentRange);

        std::vector<DataPoint> data;
        data.reserve(static_cast<size_t>(I_max_mA / I_step_mA) + 1);

        const double T_ref = 20.0;
        const double photon_energy_eV = (CONST_HC / (config_.lambda_0_nm * 1e-9)) / CONST_Q;

        for (double I_mA = 0.0; I_mA <= I_max_mA; I_mA += I_step_mA) {
            const double I_A = I_mA / 1000.0;
            double T_j = config_.T_sub_C;
            double V_val = 0.0;
            double P_opt_mW = 0.0;

            /* Самоузгоджена теплова ітерація */
            for (int iter = 0; iter < 5; ++iter) {
                V_val = photon_energy_eV + I_A * config_.R_s_ohm;
                const double I_th_mA = config_.I_th0_mA * std::exp((T_j - T_ref) / config_.T_0_K);

                if (I_mA > I_th_mA) {
                    P_opt_mW = photon_energy_eV * config_.eta_d * (I_mA - I_th_mA);
                } else {
                    P_opt_mW = 0.001 * photon_energy_eV * I_mA;
                }

                const double P_elec_mW = I_mA * V_val;
                double Q_heat_W = (P_elec_mW - P_opt_mW) / 1000.0;
                if (Q_heat_W < 0.0) Q_heat_W = 0.0;

                T_j = config_.T_sub_C + config_.R_th_KW * Q_heat_W;
            }

            const double lambda_nm = config_.lambda_0_nm + config_.dlambda_dT * (T_j - T_ref);
            const double P_elec_mW = I_mA * V_val;
            const double wpe = (P_elec_mW > 1e-6) ? (P_opt_mW / P_elec_mW) * 100.0 : 0.0;

            data.push_back(DataPoint{
                .current_mA = I_mA,
                .voltage_V = V_val,
                .power_mW = P_opt_mW,
                .temp_C = T_j,
                .lambda_nm = lambda_nm,
                .wpe_percent = wpe
            });
        }
        return data;
    }

private:
    DiodeConfig config_;
};

} // namespace laser_sim

int main() {
    using namespace laser_sim;

    DiodeConfig config{
        .lambda_0_nm = 808.0,
        .I_th0_mA = 40.0,
        .T_0_K = 140.0,
        .eta_d = 0.85,
        .R_s_ohm = 2.5,
        .R_th_KW = 35.0,
        .dlambda_dT = 0.28,
        .T_sub_C = 25.0
    };

    LaserDiodeSimulator sim(config);
    auto sim_result = sim.run(150.0, 15.0);

    if (!sim_result) {
        std::cerr << "Помилка симуляції!\n";
        return 1;
    }

    std::cout << "=== МОДЕЛЮВАННЯ ЛАЗЕРНОГО ДІОДА (C++23) ===\n";
    std::cout << std::format("{:>8} | {:>7} | {:>9} | {:>7} | {:>8} | {:>8}\n",
                             "I (мА)", "V (В)", "P (мВт)", "T (°C)", "λ (нм)", "WPE (%)");
    std::cout << "---------------------------------------------------------\n";

    for (const auto& pt : *sim_result) {
        std::cout << std::format("{:8.1f} | {:7.3f} | {:9.2f} | {:7.1f} | {:8.1f} | {:8.2f}\n",
                                 pt.current_mA, pt.voltage_V, pt.power_mW,
                                 pt.temp_C, pt.lambda_nm, pt.wpe_percent);
    }
    return 0;
}
