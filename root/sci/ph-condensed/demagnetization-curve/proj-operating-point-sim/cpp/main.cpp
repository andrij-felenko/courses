#include <iostream>
#include <cmath>
#include <algorithm>
#include <iomanip>

class PermanentMagnetModel {
private:
    double Br_20;
    double Hcj_20;
    double S;
    double mu_rec;
    double alpha_Br;
    double beta_Hcj;
    const double MU_0_SCALE = 4.0 * M_PI * 1e-4; // Тл / (кА/м)

public:
    PermanentMagnetModel(double Br, double Hcj, double S_factor = 4.5, 
                         double mu_r = 1.05, double a_Br = -0.11, double b_Hcj = -0.50)
        : Br_20(Br), Hcj_20(Hcj), S(S_factor), mu_rec(mu_r), alpha_Br(a_Br), beta_Hcj(b_Hcj) {}

    struct OperatingResult {
        double temp_C;
        double Br_t;
        double Hcj_t;
        double H_op;
        double B_op;
        double H_knee;
        bool below_knee;
        double Br_recoil;
        double delta_Br_loss;
    };

    OperatingResult calculate(double Pc, double temp_C, double H_ext = 0.0) const {
        double dt = temp_C - 20.0;
        double Br_t = std::max(0.05, Br_20 * (1.0 + (alpha_Br / 100.0) * dt));
        double Hcj_t = std::max(10.0, Hcj_20 * (1.0 + (beta_Hcj / 100.0) * dt));

        auto J_val = [&](double H) {
            double ratio = 1.0 + (H / Hcj_t);
            if (ratio < -2.0) return 0.0;
            return Br_t * std::tanh(S * ratio);
        };

        auto B_val = [&](double H) {
            return (MU_0_SCALE * H) + J_val(H);
        };

        double h_low = -Hcj_t * 1.6;
        double h_high = 0.0;

        for (int i = 0; i < 60; ++i) {
            double h_mid = (h_low + h_high) / 2.0;
            double b_mag = B_val(h_mid - H_ext);
            double b_load = Pc * (-h_mid) * MU_0_SCALE;

            if (b_mag > b_load) {
                h_high = h_mid;
            } else {
                h_low = h_mid;
            }
        }

        double h_op = (h_low + h_high) / 2.0;
        double h_net = h_op - H_ext;
        double b_op = B_val(h_net);
        double h_knee = -Hcj_t * (1.0 - (1.0 / S));

        bool is_below = (h_net < h_knee);
        double b_recoil_r = is_below ? (b_op - mu_rec * MU_0_SCALE * h_net) : Br_t;

        return {temp_C, Br_t, Hcj_t, h_op, b_op, h_knee, is_below, b_recoil_r, Br_t - b_recoil_r};
    }
};

int main() {
    PermanentMagnetModel magnet(1.30, 950.0, 5.0, 1.05, -0.12, -0.55);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== C++ Чисельне моделювання робочої точки NdFeB N42 ===\n";
    std::cout << "Температура | Br(Тл) | Hcj(кА/м) | H_op(кА/м) | B_op(Тл) | Стан\n";
    std::cout << "----------------------------------------------------------------\n";

    double temps[] = {20.0, 80.0, 120.0, 150.0};
    for (double T : temps) {
        auto res = magnet.calculate(1.2, T, 50.0);
        std::cout << "  " << std::setw(3) << (int)T << " °C     |  " 
                  << res.Br_t << "  |   " << std::setw(5) << res.Hcj_t << "   |   " 
                  << std::setw(6) << res.H_op << "   |  " << res.B_op << "  | " 
                  << (res.below_knee ? "НЕЗВОРОВНЕ РОЗМАГНІЧУВАННЯ!" : "ОК") << "\n";
    }
    return 0;
}
