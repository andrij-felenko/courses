#include "include/beam_profiler.hpp"
#include <iostream>
#include <iomanip>
#include <cmath>

int main() {
    try {
        std::cout << "=== Профілометр лазерного пучка (C++ ISO 11146) ===" << std::endl;

        const std::size_t width = 128;
        const std::size_t height = 128;
        const double pixel_pitch_um = 3.45; // 3.45 мкм / піксель

        // 1. Симуляція темнового кадру (темновий шум струму + температурний зсув ~50 ADC)
        optical::ImageFrame dark_frame(width, height);
        for (std::size_t y = 0; y < height; ++y) {
            for (std::size_t x = 0; x < width; ++x) {
                dark_frame.at(x, y) = 50 + (x % 3); // Фоновий зсув ~50 відліків
            }
        }

        // 2. Симуляція сирого кадру пучка з Ґауссовим розподілом + шум
        optical::ImageFrame raw_frame(width, height);
        const double true_x0 = 64.0;
        const double true_y0 = 64.0;
        const double true_wx = 15.0; // Радіус пучка w_x = 15 пікселів (D4σ = 30)
        const double true_wy = 12.0; // Радіус пучка w_y = 12 пікселів (D4σ = 24)

        for (std::size_t y = 0; y < height; ++y) {
            double dy = static_cast<double>(y) - true_y0;
            for (std::size_t x = 0; x < width; ++x) {
                double dx = static_cast<double>(x) - true_x0;
                
                // Ґауссова формула інтенсивності I(x,y) = I_max * exp(-2*(dx²/wx² + dy²/wy²))
                double gaussian = 1000.0 * std::exp(-2.0 * ((dx * dx) / (true_wx * true_wx) + (dy * dy) / (true_wy * true_wy)));
                uint16_t noise = dark_frame.at(x, y);
                
                raw_frame.at(x, y) = static_cast<uint16_t>(gaussian + noise);
            }
        }

        // 3. Ініціалізація аналізатора
        optical::BeamProfilerAnalyzer analyzer(pixel_pitch_um, 0.015);

        std::cout << "[1] Захоплення темнового кадру Ultracal..." << std::endl;
        analyzer.capture_dark_frame(dark_frame);

        std::cout << "[2] Обробка сирого кадру та розрахунок моментів D4σ..." << std::endl;
        optical::BeamParams params = analyzer.process_frame(raw_frame);

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "\nРезультати вимірювання пучка (ISO 11146):" << std::endl;
        std::cout << "------------------------------------------" << std::endl;
        std::cout << "Центроїд (X, Y)       : (" << params.centroid_x << ", " << params.centroid_y << ") px" << std::endl;
        std::cout << "Діаметр D4σ_x (px)    : " << params.d4sigma_x << " px (" << params.d4sigma_x * pixel_pitch_um << " мкм)" << std::endl;
        std::cout << "Діаметр D4σ_y (px)    : " << params.d4sigma_y << " px (" << params.d4sigma_y * pixel_pitch_um << " мкм)" << std::endl;
        std::cout << "Еліптичність (e)      : " << params.ellipticity << std::endl;
        std::cout << "Сумарна потужність M0 : " << params.total_power << " ADC count" << std::endl;

        // 4. Демонстрація розрахунку фактора якості M² за серією кадрів Z
        std::cout << "\n[3] Апроксимація фактора якості M² уздовж осі Z..." << std::endl;
        std::vector<optical::ZScanPoint> z_scan = {
            { 0.0,   0.210 }, // z = 0 мм
            { 20.0,  0.155 },
            { 40.0,  0.105 }, // z_waist = 40 мм (w0 = 0.0525 мм)
            { 60.0,  0.155 },
            { 80.0,  0.210 }  // z = 80 мм
        };

        double m2_factor = analyzer.compute_m2(z_scan, 632.8); // He-Ne лазер 632.8 нм
        std::cout << "Розрахований фактор M²: " << m2_factor << std::endl;

        std::cout << "\n[УСПІХ] Обробка конвеєра профілометра завершена успішно." << std::endl;

    } catch (const std::exception& ex) {
        std::cerr << "[ПОМИЛКА] " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
