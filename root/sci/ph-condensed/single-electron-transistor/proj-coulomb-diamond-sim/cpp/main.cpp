#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <algorithm>

class SingleElectronTransistor {
public:
    struct Configuration {
        double C1{1e-18};
        double C2{1e-18};
        double Cg{2e-18};
        double R1{100e3};
        double R2{100e3};
        double Temp{0.1};
    };

    explicit SingleElectronTransistor(Configuration config) 
        : cfg_(config), 
          c_total_(config.C1 + config.C2 + config.Cg),
          ec_((e_charge_ * e_charge_) / (2.0 * c_total_)) {}

    [[nodiscard]] double calculateCurrent(double Vds, double Vg, int n_max = 10) const {
        const int num_states = 2 * n_max + 1;
        std::vector<double> P(num_states, 0.0);
        std::vector<double> g1_plus(num_states), g1_minus(num_states);
        std::vector<double> g2_plus(num_states), g2_minus(num_states);

        const double Vs = Vds / 2.0;
        const double Vd = -Vds / 2.0;

        for (int i = 0; i < num_states; ++i) {
            const int n = i - n_max;
            const double n_ind = (cfg_.Cg * Vg + cfg_.C1 * Vs + cfg_.C2 * Vd) / e_charge_;
            
            const double dF1_p = ec_ * (1.0 + 2.0 * (n - n_ind)) - e_charge_ * Vs;
            const double dF1_m = ec_ * (1.0 - 2.0 * (n - n_ind)) + e_charge_ * Vs;
            const double dF2_p = ec_ * (1.0 + 2.0 * (n - n_ind)) - e_charge_ * Vd;
            const double dF2_m = ec_ * (1.0 - 2.0 * (n - n_ind)) + e_charge_ * Vd;

            g1_plus[i]  = computeRate(dF1_p, cfg_.R1);
            g1_minus[i] = computeRate(dF1_m, cfg_.R1);
            g2_plus[i]  = computeRate(dF2_p, cfg_.R2);
            g2_minus[i] = computeRate(dF2_m, cfg_.R2);
        }

        P[n_max] = 1.0;
        for (int i = n_max; i < num_states - 1; ++i) {
            const double W_p = g1_plus[i] + g2_plus[i];
            const double W_m = g1_minus[i + 1] + g2_minus[i + 1];
            if (W_m > 0.0) P[i + 1] = P[i] * (W_p / W_m);
        }
        for (int i = n_max; i > 0; --i) {
            const double W_m = g1_minus[i] + g2_minus[i];
            const double W_p = g1_plus[i - 1] + g2_plus[i - 1];
            if (W_p > 0.0) P[i - 1] = P[i] * (W_m / W_p);
        }

        double sum_P = 0.0;
        for (double val : P) sum_P += val;
        if (sum_P > 0.0) {
            for (double& val : P) val /= sum_P;
        }

        double I_ds = 0.0;
        for (int i = 0; i < num_states; ++i) {
            I_ds += e_charge_ * P[i] * (g1_plus[i] - g1_minus[i]);
        }
        return I_ds;
    }

private:
    static constexpr double e_charge_ = 1.602176634e-19;
    static constexpr double kb_const_ = 1.380649e-23;

    Configuration cfg_;
    double c_total_;
    double ec_;

    [[nodiscard]] double computeRate(double delta_F, double R_tunnel) const {
        if (std::abs(delta_F) < 1e-30) {
            return (kb_const_ * cfg_.Temp) / (e_charge_ * e_charge_ * R_tunnel);
        }
        const double arg = delta_F / (kb_const_ * cfg_.Temp);
        if (arg > 100.0) return 0.0;
        if (arg < -100.0) return -delta_F / (e_charge_ * e_charge_ * R_tunnel);
        return delta_F / (e_charge_ * e_charge_ * R_tunnel * (1.0 - std::exp(-arg)));
    }
};

int main() {
    SingleElectronTransistor::Configuration cfg;
    cfg.Temp = 0.05; // 50 мілікельвінів
    SingleElectronTransistor set_sim(cfg);

    double current = set_sim.calculateCurrent(0.01, 0.02);
    std::cout << "Розрахований струм SET: " << current * 1e9 << " нА\n";
    return 0;
}
