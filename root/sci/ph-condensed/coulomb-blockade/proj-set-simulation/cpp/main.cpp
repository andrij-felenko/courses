#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <algorithm>
#include <iomanip>

struct SetParameters {
    double C_s{1.0e-18};   // Farads
    double C_d{1.0e-18};   // Farads
    double C_g{0.5e-18};   // Farads
    double R_s{100.0e3};   // Ohms
    double R_d{100.0e3};   // Ohms
    double T{0.1};         // Kelvin
};

class SingleElectronTransistor {
public:
    explicit SingleElectronTransistor(const SetParameters& params)
        : m_params(params),
          m_C_sum(params.C_s + params.C_d + params.C_g),
          m_E_c((m_e * m_e) / (2.0 * m_C_sum)) {}

    [[nodiscard]] double calculate_rate(double delta_E, double R_T) const {
        if (m_params.T < 1.0e-6) {
            return (delta_E < 0.0) ? -delta_E / ((m_e * m_e) * R_T) : 0.0;
        }

        const double x = delta_E / (m_kB * m_params.T);
        if (x > 100.0) {
            return 0.0;
        }
        if (x < -100.0) {
            return -delta_E / ((m_e * m_e) * R_T);
        }
        if (std::abs(x) < 1.0e-6) {
            return (m_kB * m_params.T) / ((m_e * m_e) * R_T);
        }

        return -delta_E / (((m_e * m_e) * R_T) * (1.0 - std::exp(x)));
    }

    [[nodiscard]] double calculate_current(double V_ds, double V_g, int N_max = 10) const {
        const int dim = 2 * N_max + 1;
        const double n_g = (m_params.C_g * V_g) / m_e;

        std::vector<double> gamma_s_plus(dim, 0.0);
        std::vector<double> gamma_s_minus(dim, 0.0);
        std::vector<double> gamma_d_plus(dim, 0.0);
        std::vector<double> gamma_d_minus(dim, 0.0);

        for (int i = 0; i < dim; ++i) {
            const int n = i - N_max;

            // ΔE_s+ (n -> n+1 from Source)
            const double dE_sp = m_E_c * (1.0 + 2.0 * (n - n_g)) - m_e * V_ds * (m_params.C_d + m_params.C_g / 2.0) / m_C_sum;
            gamma_s_plus[i] = calculate_rate(dE_sp, m_params.R_s);

            // ΔE_s- (n -> n-1 to Source)
            const double dE_sm = m_E_c * (1.0 - 2.0 * (n - n_g)) + m_e * V_ds * (m_params.C_d + m_params.C_g / 2.0) / m_C_sum;
            gamma_s_minus[i] = calculate_rate(dE_sm, m_params.R_s);

            // ΔE_d+ (n -> n+1 from Drain)
            const double dE_dp = m_E_c * (1.0 + 2.0 * (n - n_g)) + m_e * V_ds * (m_params.C_s + m_params.C_g / 2.0) / m_C_sum;
            gamma_d_plus[i] = calculate_rate(dE_dp, m_params.R_d);

            // ΔE_d- (n -> n-1 to Drain)
            const double dE_dm = m_E_c * (1.0 - 2.0 * (n - n_g)) - m_e * V_ds * (m_params.C_s + m_params.C_g / 2.0) / m_C_sum;
            gamma_d_minus[i] = calculate_rate(dE_dm, m_params.R_d);
        }

        // Обчислення співвідношень P(n+1)/P(n)
        std::vector<double> ratio(dim - 1, 0.0);
        for (int i = 0; i < dim - 1; ++i) {
            const double denom = gamma_s_minus[i + 1] + gamma_d_minus[i + 1];
            const double num = gamma_s_plus[i] + gamma_d_plus[i];
            ratio[i] = (denom > 0.0) ? (num / denom) : 0.0;
        }

        // Нормування векторного розподілу ймовірностей P(n)
        std::vector<double> P(dim, 0.0);
        P[0] = 1.0;
        for (std::size_t i = 1; i < P.size(); ++i) {
            P[i] = P[i - 1] * ratio[i - 1];
        }

        const double p_sum = std::accumulate(P.begin(), P.end(), 0.0);
        if (p_sum > 0.0) {
            for (double& p : P) {
                p /= p_sum;
            }
        }

        // Сумарний струм через витоковий контакт
        double current = 0.0;
        for (std::size_t i = 0; i < static_cast<std::size_t>(dim); ++i) {
            current += P[i] * (gamma_s_plus[i] - gamma_s_minus[i]);
        }

        return m_e * current;
    }

private:
    static constexpr double m_e{1.602176634e-19};
    static constexpr double m_kB{1.380649e-23};

    SetParameters m_params;
    double m_C_sum;
    double m_E_c;
};

int main() {
    SetParameters params;
    params.T = 0.05; // 50 mK
    
    SingleElectronTransistor set_sim(params);
    const double I_val = set_sim.calculate_current(0.001, 0.002);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Струм SET при V_ds=1 мВ, V_g=2 мВ: " << I_val * 1.0e9 << " нА\n";

    return 0;
}
