#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <span>

namespace pcm {
    constexpr std::size_t GRID_SIZE = 100;
    constexpr double DX = 1.0e-9;        // 1 нм
    constexpr double DT = 1.0e-12;       // 1 пс

    constexpr double DENSITY = 6150.0;
    constexpr double SPECIFIC_HEAT = 202.0;
    constexpr double T_MELT = 888.0;    // 615 °C
    constexpr double T_GLASS = 473.0;   // 200 °C
    constexpr double T_AMB = 300.0;

    class PcmCellSimulator {
    private:
        std::vector<double> m_temp;
        std::vector<double> m_k_th;
        std::vector<double> m_rho;

    public:
        PcmCellSimulator()
            : m_temp(GRID_SIZE, T_AMB),
              m_k_th(GRID_SIZE, 0.5),
              m_rho(GRID_SIZE, 1.0e-5) {}

        void runPulse(double currentDensity, double durationNs) {
            const std::size_t steps = static_cast<std::size_t>(durationNs * 1.0e-9 / DT);
            std::vector<double> nextTemp = m_temp;

            for (std::size_t step = 0; step < steps; ++step) {
                for (std::size_t i = 1; i < GRID_SIZE - 1; ++i) {
                    const double heatConduction = m_k_th[i] * (m_temp[i+1] - 2.0 * m_temp[i] + m_temp[i-1]) / (DX * DX);
                    const double jouleHeating = currentDensity * currentDensity * m_rho[i];
                    
                    const double dT = (DT / (DENSITY * SPECIFIC_HEAT)) * (heatConduction + jouleHeating);
                    nextTemp[i] = m_temp[i] + dT;
                }
                nextTemp[0] = T_AMB;
                nextTemp[GRID_SIZE - 1] = T_AMB;
                m_temp = nextTemp;
            }
        }

        [[nodiscard]] double getMaxTemperature() const noexcept {
            return *std::max_element(m_temp.begin(), m_temp.end());
        }

        [[nodiscard]] std::span<const double> getTemperatureProfile() const noexcept {
            return m_temp;
        }
    };
}

int main() {
    pcm::PcmCellSimulator simulator;

    std::cout << "=== Обчислення теплового профілю імпульсу SET/RESET (C++) ===\n";
    simulator.runPulse(5.0e11, 10.0); // 10 нс імпульс

    const double maxTemp = simulator.getMaxTemperature();
    std::cout << "Пікова температура гарячої точки: " << maxTemp << " K\n";

    if (maxTemp > pcm::T_MELT) {
        std::cout << "Стан: Перевищено порог плавлення T_m (" << pcm::T_MELT << " K). Матеріал розплавлений.\n";
    } else if (maxTemp > pcm::T_GLASS) {
        std::cout << "Стан: Температура у вікні кристалізації (T_g < T < T_m).\n";
    } else {
        std::cout << "Стан: Температура нижче порогу склування.\n";
    }

    return 0;
}
