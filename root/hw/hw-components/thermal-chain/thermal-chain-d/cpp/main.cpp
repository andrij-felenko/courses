#include <iostream>
#include <vector>
#include <array>
#include <iomanip>

struct ThermalLayer {
    double resistance{0.0};  // Тепловий опір [°C/Вт]
    double capacitance{0.0}; // Теплова ємність [Дж/°C]
};

class CauerThermalNetwork {
public:
    explicit CauerThermalNetwork(std::vector<ThermalLayer> layers, double initial_temp)
        : layers_(std::move(layers)), temps_(layers_.size(), initial_temp) {}

    void step(double power_in, double ambient_temp, double dt) {
        const size_t n = layers_.size();
        std::vector<double> heat_flows(n);

        // Розрахунок теплових потоків крізь послідовні резистори
        for (size_t i = 0; i < n - 1; ++i) {
            heat_flows[i] = (temps_[i] - temps_[i + 1]) / layers_[i].resistance;
        }
        heat_flows[n - 1] = (temps_[n - 1] - ambient_temp) / layers_[n - 1].resistance;

        // Оновлення температур у ємнісних вузлах
        temps_[0] += ((power_in - heat_flows[0]) / layers_[0].capacitance) * dt;
        for (size_t i = 1; i < n; ++i) {
            temps_[i] += ((heat_flows[i - 1] - heat_flows[i]) / layers_[i].capacitance) * dt;
        }
    }

    [[nodiscard]] double junction_temp() const noexcept { return temps_.front(); }
    [[nodiscard]] double case_temp() const noexcept { return temps_.back(); }

private:
    std::vector<ThermalLayer> layers_;
    std::vector<double> temps_;
};

int main() {
    // 3-ланкова модель Кауера для силового транзистора
    std::vector<ThermalLayer> mosfet_layers = {
        { 0.095, 1.85e-3 },  // Кристал кремнію
        { 0.345, 2.10e-2 },  // Припій die attach
        { 0.560, 2.15e-1 }   // Мідний фланець
    };

    constexpr double ambient_temp = 25.0;
    CauerThermalNetwork thermal_sim(mosfet_layers, ambient_temp);

    constexpr double dt = 1e-5;            // Крок інтегрування 10 мкс
    constexpr double sim_time = 0.05;      // 50 мс
    constexpr double pulse_power = 200.0;  // 200 Вт імпульс
    constexpr double pulse_duration = 0.01;// 10 мс

    const auto total_steps = static_cast<size_t>(sim_time / dt);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Час [мс]\tПотужність [Вт]\tT_кристал [°C]\tT_фланець [°C]\n";

    for (size_t i = 0; i <= total_steps; ++i) {
        const double t = static_cast<double>(i) * dt;
        const double power = (t <= pulse_duration) ? pulse_power : 0.0;

        thermal_sim.step(power, ambient_temp, dt);

        if (i % 200 == 0) {  // Вивід кожні 2 мс
            std::cout << t * 1000.0 << "\t\t"
                      << power << "\t\t"
                      << thermal_sim.junction_temp() << "\t\t"
                      << thermal_sim.case_temp() << "\n";
        }
    }

    return 0;
}
