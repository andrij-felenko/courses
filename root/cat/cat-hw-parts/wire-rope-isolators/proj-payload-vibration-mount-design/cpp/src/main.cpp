#include "VibrationMonitor.hpp"
#include <iostream>
#include <cmath>
#include <iomanip>

int main() {
    std::cout << "Ініціалізація ООП-модуля моніторингу віброізоляції підвісу...\n";

    VibrationMonitor monitor(10.0, 2.2);

    std::cout << "Симуляція вібраційного навантаження (проходження частотного резонансу та зони ізоляції)...\n";
    std::cout << "Час (с) | Частота (Гц) | Рама (G) | Підвіс (G) | Коефіцієнт T | Стан\n";
    std::cout << "--------------------------------------------------------------------\n";

    for (int step = 1; step <= 80; ++step) {
        double t = step * 0.05; // Крок 50 мс
        double freq = 5.0 + (step / 80.0) * 45.0; // Частота від 5 до 50 Гц
        double omega = 2.0 * 3.1415926535 * freq;

        // Вібрація рами носія амплітудою 2.0 G
        double a_frame = 2.0 * std::sin(omega * t);

        // Динамічний відгук підвісу (резонанс біля 18 Гц)
        double r = freq / 18.0;
        double zeta = 0.18;
        double t_dyn = std::sqrt((1.0 + std::pow(2.0 * zeta * r, 2)) /
                                 (std::pow(1.0 - r * r, 2) + std::pow(2.0 * zeta * r, 2)));
        double a_payload = a_frame * t_dyn;

        monitor.recordFrameSample(t, 0.0, 0.0, a_frame);
        monitor.recordPayloadSample(t, 0.0, 0.0, a_payload);

        if (step % 10 == 0 || (freq >= 17.0 && freq <= 19.5)) {
            std::cout << "  " << std::fixed << std::setprecision(2) << t << " с |   " 
                      << std::setw(5) << std::setprecision(1) << freq << " Гц   |  " 
                      << std::setw(5) << std::setprecision(2) << std::abs(a_frame) << " G |   " 
                      << std::setw(5) << std::setprecision(2) << std::abs(a_payload) << " G |    " 
                      << std::setw(5) << std::setprecision(2) << t_dyn << "    | "
                      << (t_dyn > 2.0 ? "[РЕЗОНАНС]" : (t_dyn < 0.6 ? "[ІЗОЛЯЦІЯ]" : "[ПЕРЕХІДНИЙ]")) << "\n";
        }
    }

    monitor.printTelemetryReport();
    return 0;
}
