// thermo_sim.cpp - Ідіоматичний чисельний симулятор термодинамічних процесів мовою C++23
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <expected>
#include <string_view>

namespace thermo {

constexpr double R_GAS = 8.314462618;

enum class ProcessType {
    Isochoric,
    Isobaric,
    Isothermal,
    Adiabatic
};

struct State {
    double p{0.0}; // Тиск [Па]
    double v{0.0}; // Об'єм [м³]
    double t{0.0}; // Температура [К]
};

struct ProcessStep {
    ProcessType type;
    State start;
    State end;
    double work{0.0};   // W [Дж]
    double heat{0.0};   // Q [Дж]
    double delta_u{0.0};// dU [Дж]
};

class GasModel {
public:
    explicit GasModel(double moles, double degrees_of_freedom)
        : moles_(moles), dof_(degrees_of_freedom) {}

    [[nodiscard]] double moles() const noexcept { return moles_; }
    [[nodiscard]] double c_v() const noexcept { return (dof_ / 2.0) * R_GAS; }
    [[nodiscard]] double c_p() const noexcept { return c_v() + R_GAS; }
    [[nodiscard]] double gamma() const noexcept { return c_p() / c_v(); }

    [[nodiscard]] State state_from_pv(double p, double v) const {
        return State{.p = p, .v = v, .t = (p * v) / (moles_ * R_GAS)};
    }

private:
    double moles_;
    double dof_;
};

enum class SimError {
    InvalidVolume,
    InvalidTemperature,
    ZeroDivision
};

class CycleSimulator {
public:
    explicit CycleSimulator(GasModel gas) : gas_(std::move(gas)) {}

    [[nodiscard]] std::expected<ProcessStep, SimError> 
    step_isothermal(const State& start, double target_v) const {
        if (target_v <= 0.0 || start.v <= 0.0) return std::unexpected(SimError::InvalidVolume);
        
        State end{.p = (gas_.moles() * R_GAS * start.t) / target_v,
                  .v = target_v,
                  .t = start.t};
        
        double w = gas_.moles() * R_GAS * start.t * std::log(target_v / start.v);
        return ProcessStep{
            .type = ProcessType::Isothermal,
            .start = start,
            .end = end,
            .work = w,
            .heat = w,
            .delta_u = 0.0
        };
    }

    [[nodiscard]] std::expected<ProcessStep, SimError>
    step_adiabatic(const State& start, double target_v) const {
        if (target_v <= 0.0 || start.v <= 0.0) return std::unexpected(SimError::InvalidVolume);

        double target_p = start.p * std::pow(start.v / target_v, gas_.gamma());
        double target_t = (target_p * target_v) / (gas_.moles() * R_GAS);

        State end{.p = target_p, .v = target_v, .t = target_t};
        double du = gas_.moles() * gas_.c_v() * (target_t - start.t);

        return ProcessStep{
            .type = ProcessType::Adiabatic,
            .start = start,
            .end = end,
            .work = -du,
            .heat = 0.0,
            .delta_u = du
        };
    }

    void add_step(ProcessStep step) {
        steps_.push_back(step);
    }

    void print_report() const {
        double total_work{0.0};
        double q_in{0.0};
        double q_out{0.0};
        double total_du{0.0};

        std::cout << "=== СИМУЛЯЦІЯ ТЕРМОДИНАМІЧНОГО ЦИКЛУ (C++) ===\n";
        std::cout << std::fixed << std::setprecision(2);
        
        for (std::size_t i = 0; i < steps_.size(); ++i) {
            const auto& s = steps_[i];
            std::cout << "Крок " << i + 1 << ": W = " << std::setw(9) << s.work 
                      << " Дж, Q = " << std::setw(9) << s.heat 
                      << " Дж, dU = " << std::setw(9) << s.delta_u << " Дж\n";
            total_work += s.work;
            total_du += s.delta_u;
            if (s.heat > 0) q_in += s.heat;
            else q_out += -s.heat;
        }

        double eta = (q_in > 0) ? (total_work / q_in) * 100.0 : 0.0;
        std::cout << "---------------------------------------------\n";
        std::cout << "Корисна мережева робота W_net : " << std::setw(10) << total_work << " Дж\n";
        std::cout << "Сумарне підведене тепло Q_in   : " << std::setw(10) << q_in << " Дж\n";
        std::cout << "Сумарне відведене тепло Q_out  : " << std::setw(10) << q_out << " Дж\n";
        std::cout << "Збереження енергії sum(dU)    : " << std::setw(10) << total_du << " Дж\n";
        std::cout << "Термічний ККД (eta)           : " << std::setw(10) << eta << " %\n";
    }

private:
    GasModel gas_;
    std::vector<ProcessStep> steps_;
};

} // namespace thermo

int main() {
    using namespace thermo;
    
    // Двохатомний газ (повітря, 1 моль, i = 5)
    GasModel air(1.0, 5.0);
    CycleSimulator sim(air);

    State s1 = air.state_from_pv(500'000.0, 0.002);

    auto step1 = sim.step_isothermal(s1, 0.006);
    if (!step1) return 1;
    sim.add_step(*step1);

    auto step2 = sim.step_adiabatic(step1->end, 0.012);
    if (!step2) return 1;
    sim.add_step(*step2);

    auto step3 = sim.step_isothermal(step2->end, 0.004);
    if (!step3) return 1;
    sim.add_step(*step3);

    auto step4 = sim.step_adiabatic(step3->end, 0.002);
    if (!step4) return 1;
    sim.add_step(*step4);

    sim.print_report();
    return 0;
}
