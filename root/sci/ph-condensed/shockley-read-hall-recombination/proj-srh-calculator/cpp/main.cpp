#include <iostream>
#include <cmath>
#include <vector>
#include <optional>
#include <iomanip>

namespace physics {

struct SRHTrapParams {
    double et_minus_ei_ev{0.0}; // E_t - E_i в еВ
    double tau_n0_s{1e-6};      // τ_n0 в с
    double tau_p0_s{1e-6};      // τ_p0 в с
};

struct SRHResult {
    double r_srh{0.0};          // см⁻³·с⁻¹
    double tau_eff_s{0.0};      // с
    bool is_generation{false};
};

class SRHCalculator {
public:
    static constexpr double K_B_EV = 8.617333e-5;
    
    explicit SRHCalculator(SRHTrapParams params, double temp_k = 300.0, double n_i = 1.5e10)
        : params_(params), temp_k_(temp_k), n_i_(n_i) {}

    [[nodiscard]] std::optional<SRHResult> compute(double n, double p) const noexcept {
        if (n < 0.0 || p < 0.0) return std::nullopt;
        
        const double vt = K_B_EV * temp_k_;
        const double exp_factor = std::exp(params_.et_minus_ei_ev / vt);
        const double n_1 = n_i_ * exp_factor;
        const double p_1 = n_i_ / exp_factor;
        
        const double ni_sq = n_i_ * n_i_;
        const double numerator = n * p - ni_sq;
        const double denominator = params_.tau_p0_s * (n + n_1) + params_.tau_n0_s * (p + p_1);
        
        if (denominator <= 0.0) return std::nullopt;
        
        SRHResult res;
        res.r_srh = numerator / denominator;
        res.is_generation = (numerator < 0.0);
        
        const double delta_n = std::max(n - (ni_sq / std::max(p, 1.0)), 1e-12);
        res.tau_eff_s = (res.r_srh > 0.0) ? (delta_n / res.r_srh) : 0.0;
        
        return res;
    }

private:
    SRHTrapParams params_;
    double temp_k_;
    double n_i_;
};

} // namespace physics

int main() {
    using namespace physics;
    
    const SRHTrapParams midgap_trap{ .et_minus_ei_ev = 0.0, .tau_n0_s = 1e-6, .tau_p0_s = 1.0e-6 };
    const SRHCalculator calc(midgap_trap, 300.0, 1.5e10);
    
    const double p0 = 1e16;
    const double n_i = 1.5e10;
    
    std::cout << std::scientific << std::setprecision(2);
    std::cout << "--- (C++) SRH Injection Level Sweep ---\n";
    
    for (int exp = 10; exp <= 17; ++exp) {
        const double dn = std::pow(10.0, exp);
        const double n = (n_i * n_i / p0) + dn;
        const double p = p0 + dn;
        
        if (auto res = calc.compute(n, p)) {
            std::cout << "Δn = " << dn << " cm⁻³ | R_SRH = " << res->r_srh 
                      << " cm⁻³s⁻¹ | τ_eff = " << std::fixed << std::setprecision(3) 
                      << (res->tau_eff_s * 1e6) << " µs\n" << std::scientific;
        }
    }
    
    return 0;
}
