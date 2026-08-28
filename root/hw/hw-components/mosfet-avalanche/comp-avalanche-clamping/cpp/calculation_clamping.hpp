// calculation_clamping.hpp / .cpp — ідіоматичний C++20 розрахунок методів гасіння
#include <iostream>
#include <expected>
#include <string_view>
#include <format>

struct CircuitParams {
    double v_dd{24.0};         // Напруга живлення, В
    double l_ind{0.010};       // Індуктивність, Гн (10 мГн)
    double i_peak{3.0};        // Струм навантаження, А
    double r_coil{8.0};        // Опір обмотки, Ом
    double bv_dss{60.0};       // Напруга лавини MOSFET, В
    double v_tvs_clamp{45.0};  // Напруга фіксації TVS, В
};

struct DemagResult {
    double t_demag_sec{0.0};
    double energy_joules{0.0};
    double peak_power_w{0.0};
};

enum class CalcError {
    InvalidVoltageDifference,
    ZeroInductance
};

class ClampingCalculator {
public:
    static std::expected<DemagResult, CalcError> calc_avalanche(const CircuitParams& p) noexcept {
        if (p.l_ind <= 0.0) return std::unexpected(CalcError::ZeroInductance);
        const double v_diff = p.bv_dss - p.v_dd;
        if (v_diff <= 0.0) return std::unexpected(CalcError::InvalidVoltageDifference);

        const double t_av = (p.l_ind * p.i_peak) / v_diff;
        const double e_as = 0.5 * p.l_ind * p.i_peak * p.i_peak * (p.bv_dss / v_diff);
        const double p_pk = p.bv_dss * p.i_peak;

        return DemagResult{t_av, e_as, p_pk};
    }

    static std::expected<DemagResult, CalcError> calc_freewheel(const CircuitParams& p, double v_f = 0.7) noexcept {
        if (p.l_ind <= 0.0) return std::unexpected(CalcError::ZeroInductance);
        const double effective_r = (p.r_coil > 0.05) ? p.r_coil : 0.05;
        const double tau = p.l_ind / effective_r;
        const double t_demag = 5.0 * tau; // 99% спаду струму
        const double energy = 0.5 * p.l_ind * p.i_peak * p.i_peak;
        const double p_pk = v_f * p.i_peak;

        return DemagResult{t_demag, energy, p_pk};
    }

    static std::expected<DemagResult, CalcError> calc_tvs(const CircuitParams& p) noexcept {
        if (p.l_ind <= 0.0) return std::unexpected(CalcError::ZeroInductance);
        const double v_diff = p.v_tvs_clamp - p.v_dd;
        if (v_diff <= 0.0) return std::unexpected(CalcError::InvalidVoltageDifference);

        const double t_demag = (p.l_ind * p.i_peak) / v_diff;
        const double energy = 0.5 * p.l_ind * p.i_peak * p.i_peak * (p.v_tvs_clamp / v_diff);
        const double p_pk = p.v_tvs_clamp * p.i_peak;

        return DemagResult{t_demag, energy, p_pk};
    }
};
