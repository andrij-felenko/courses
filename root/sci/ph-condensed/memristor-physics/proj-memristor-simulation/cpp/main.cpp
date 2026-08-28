#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

// Параметри фізичної моделі мемристора HP TiO2
struct MemristorParams {
    double r_on = 100.0;          // Опір ON стану (Ом)
    double r_off = 16000.0;       // Опір OFF стану (Ом)
    double d = 10e-9;             // Товщина плівки D (м)
    double mu_v = 1e-14;          // Рухливість вакансій (м^2 / V s)
    int p_window = 2;             // Показник степеня віконної функції Biolek
};

// Стан мемристора під час моделювання
struct MemristorState {
    double x = 0.1;               // Нормована ширина w/D у діапазоні [0, 1]
};

// Віконна функція Біолека для усунення граничного блокування
double biolek_window(double x, double current, int p) {
    double stp = (current < 0.0) ? 1.0 : 0.0;
    double base = x - stp;
    return 1.0 - std::pow(base, 2 * p);
}

// Похідна стану dx/dt
double state_derivative(double x, double current, const MemristorParams& p) {
    double k = (p.mu_v * p.r_on) / (p.d * p.d);
    double win = biolek_window(x, current, p.p_window);
    return k * current * win;
}

// Поточний опір R(x)
double current_resistance(double x, const MemristorParams& p) {
    return p.r_on * x + p.r_off * (1.0 - x);
}

// Результат одного кроку моделювання
struct SimulationPoint {
    double time;
    double voltage;
    double current;
    double resistance;
    double x_state;
};

// Головна функція моделювання синусоїдної напруги (Метод Ейлера)
std::vector<SimulationPoint> simulate_memristor(
    double v_amplitude, 
    double frequency_hz, 
    double total_time_s, 
    double dt_s,
    MemristorParams params,
    MemristorState initial_state) 
{
    std::vector<SimulationPoint> results;
    size_t num_steps = static_cast<size_t>(total_time_s / dt_s);
    results.reserve(num_steps);

    MemristorState state = initial_state;
    double omega = 2.0 * M_PI * frequency_hz;

    for (size_t step = 0; step < num_steps; ++step) {
        double t = step * dt_s;
        double v = v_amplitude * std::sin(omega * t);

        double r_curr = current_resistance(state.x, params);
        double i = v / r_curr;

        results.push_back({t, v, i, r_curr, state.x});

        // Оновлення стану за методом Ейлера
        double dxdt = state_derivative(state.x, i, params);
        state.x += dxdt * dt_s;

        // Обмеження стану строго в інтервалі [0, 1]
        if (state.x < 0.0) state.x = 0.0;
        if (state.x > 1.0) state.x = 1.0;
    }

    return results;
}

int main() {
    MemristorParams params;
    MemristorState init_state{0.1}; // Початковий стан: високий опір (x = 0.1)

    double v_peak = 1.2;            // Амплітуда напруги 1.2 В
    double freq = 2.0;              // Частота 2 Гц
    double sim_time = 1.0;          // Час моделювання 1.0 с
    double dt = 0.0001;             // Крок за часом 0.1 мс

    auto trace = simulate_memristor(v_peak, freq, sim_time, dt, params, init_state);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "t (s)\tV (V)\tI (mA)\tR (kOhm)\tx (w/D)\n";
    std::cout << "--------------------------------------------------\n";

    // Вивід кожної 500-ї точки для наочності
    for (size_t i = 0; i < trace.size(); i += 500) {
        const auto& pt = trace[i];
        std::cout << pt.time << "\t" 
                  << pt.voltage << "\t" 
                  << pt.current * 1e3 << "\t" 
                  << pt.resistance / 1e3 << "\t" 
                  << pt.x_state << "\n";
    }

    return 0;
}
