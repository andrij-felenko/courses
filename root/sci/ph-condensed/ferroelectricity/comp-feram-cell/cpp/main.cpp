// Simulation of 1T-1C FeRAM Read & Write Cycles in C++17
#include <iostream>
#include <iomanip>
#include <algorithm>

class FeramCell {
public:
    enum class State { Logic0, Logic1 };

    FeramCell(double area_um2, double P_r_uC_cm2, double C_cell_fF, State state)
        : area_um2_(area_um2), P_r_uC_cm2_(P_r_uC_cm2), C_cell_fF_(C_cell_fF), state_(state) {}

    [[nodiscard]] double read_destructive(double C_bl_fF, double V_dd_volts, double temp_C) {
        const double p_r_eff = std::max(0.0, P_r_uC_cm2_ * (1.0 - 0.0015 * (temp_C - 25.0)));
        const double area_cm2 = area_um2_ * 1e-8;

        const double Q_linear_pC = (C_cell_fF_ * 1e-3) * V_dd_volts;
        const double Q_switch_pC = (state_ == State::Logic1)
            ? (2.0 * p_r_eff * (area_cm2 * 1e6))
            : 0.0;

        const double Q_total_pC = Q_linear_pC + Q_switch_pC;
        const double total_cap_fF = C_bl_fF + C_cell_fF_;
        const double V_bl = (Q_total_pC * 1e3) / (total_cap_fF * 1e-3);

        // Destructive read resets cell to Logic0 (+Pr)
        state_ = State::Logic0;

        return V_bl;
    }

    [[nodiscard]] State get_state() const noexcept { return state_; }

private:
    double area_um2_;
    double P_r_uC_cm2_;
    double C_cell_fF_;
    State state_;
};

int main() {
    constexpr double C_bl_fF = 150.0;
    constexpr double V_dd = 1.8;
    constexpr double Temp = 85.0; // 85 C operating temperature

    FeramCell cell1(0.05, 22.0, 12.0, FeramCell::State::Logic1);
    FeramCell cell0(0.05, 22.0, 12.0, FeramCell::State::Logic0);

    const double v1 = cell1.read_destructive(C_bl_fF, V_dd, Temp);
    const double v0 = cell0.read_destructive(C_bl_fF, V_dd, Temp);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "FeRAM Read State '1' at 85C: V_BL1 = " << v1 << " V\n";
    std::cout << "FeRAM Read State '0' at 85C: V_BL0 = " << v0 << " V\n";
    std::cout << "Sense Margin ΔV_BL = " << (v1 - v0) << " V\n";

    return 0;
}
