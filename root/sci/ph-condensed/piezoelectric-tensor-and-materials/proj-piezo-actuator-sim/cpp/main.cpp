#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

namespace piezo {

struct ActuatorParams {
    double d33{450e-12};        // П'єзомодуль, м/В
    double K_p{40e6};           // Жорсткість стека, Н/м
    double C0{2.2e-6};          // Електрична ємність, Ф
    std::size_t num_layers{120};// Кількість шарів N
    double mass{0.25};          // Навантажувальна маса, кг
    double damping{200.0};      // Демпфування, Н·с/м
    double k_ext{2e6};          // Зовнішня жорсткість, Н/м
    
    // Коефіцієнти гістерезису Бука-Вена
    double bw_alpha{0.25};
    double bw_beta{0.15};
    double bw_gamma{0.10};
};

struct SimulationState {
    double position{0.0};       // Зсув x, м
    double velocity{0.0};       // Швидкість v, м/с
    double hyst_state{0.0};     // Стан гістерезису h
    double charge{0.0};         // Заряд Q, Кл
};

class PiezoActuatorSimulator {
public:
    explicit PiezoActuatorSimulator(ActuatorParams params)
        : params_{std::move(params)} {}

    [[nodiscard]] SimulationState step(const SimulationState& current, double voltage, double dt) const noexcept {
        SimulationState next = current;

        // 1. Електромеханічна сила
        const double F_piezo = params_.num_layers * params_.d33 * params_.K_p * voltage;

        // 2. Гістерезисна складова (метод Рунге-Кутти 2-го порядку для h)
        const double v = current.velocity;
        const double h = current.hyst_state;
        const double dh_dt = params_.bw_alpha * v 
                           - params_.bw_beta * std::abs(v) * h 
                           - params_.bw_gamma * v * std::abs(h);
        next.hyst_state = h + dh_dt * dt;

        // 3. Динамічний баланс сил
        const double F_net = F_piezo 
                           - (params_.K_p + params_.k_ext) * current.position 
                           - params_.damping * v 
                           - next.hyst_state * params_.K_p * 0.1;

        // 4. Інтегрування за схемою Ейлера-Кромара
        const double accel = F_net / params_.mass;
        next.velocity = current.velocity + accel * dt;
        next.position = current.position + next.velocity * dt;

        // 5. Повний заряд
        next.charge = params_.C0 * voltage + params_.num_layers * params_.d33 * (params_.K_p * next.position);

        return next;
    }

private:
    ActuatorParams params_;
};

} // namespace piezo

int main() {
    using namespace piezo;

    const ActuatorParams params;
    const PiezoActuatorSimulator simulator(params);

    SimulationState state;
    constexpr double dt = 1e-6;
    constexpr double t_max = 0.01;
    constexpr double freq = 200.0;
    constexpr double V_amp = 100.0;

    const std::size_t total_steps = static_cast<std::size_t>(t_max / dt);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Час(мс)\tНапруга(В)\tЗсув(мкм)\tЗаряд(мкКл)\n";

    for (std::size_t step_idx = 0; step_idx < total_steps; ++step_idx) {
        const double t = step_idx * dt;
        const double voltage = V_amp * std::sin(2.0 * std::numbers::pi * freq * t);

        state = simulator.step(state, voltage, dt);

        if (step_idx % 500 == 0) {
            std::cout << (t * 1000.0) << "\t" 
                      << voltage << "\t" 
                      << (state.position * 1e6) << "\t" 
                      << (state.charge * 1e6) << "\n";
        }
    }

    return 0;
}
