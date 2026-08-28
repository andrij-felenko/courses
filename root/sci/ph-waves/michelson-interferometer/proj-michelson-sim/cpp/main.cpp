#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <fstream>
#include <iomanip>

// Конфігураційна структура параметрів інтерферометра
struct MichelsonConfig {
    double wavelength_m = 632.8e-9;   // довжина хвилі лазера (He-Ne)
    double delta_L_m = 10.0e-6;       // початкова різниця плечей d0 (10 мкм)
    double wedge_alpha = 15.0e-6;     // кут клина alpha (15 мкрад)
    double R_m = 0.5;                 // радіус кривизни хвильового фронту (0.5 м)
    double beam_radius_m = 0.003;     // радіус гаусового пучка w0 (3 мм)
    int width = 64;                   // ширина сітки (пікселі)
    int height = 32;                  // висота сітки (пікселі)
};

class MichelsonSimulator {
public:
    explicit MichelsonSimulator(const MichelsonConfig& config) : config_(config) {}

    // Генерація текстового псевдографічного зображення для консолі
    std::vector<std::string> renderAscii() const {
        const std::string ascii_chars = " .:-=+*#%@";
        std::vector<std::string> output;
        output.reserve(config_.height);

        const double scale_x = 0.006 / config_.width;
        const double scale_y = 0.006 / config_.height;

        for (int py = 0; py < config_.height; ++py) {
            const double y = (py - config_.height / 2.0) * scale_y;
            std::string row;
            row.reserve(config_.width);

            for (int px = 0; px < config_.width; ++px) {
                const double x = (px - config_.width / 2.0) * scale_x;

                // 1. Оптична різниця ходу Delta_s(x, y)
                const double delta_s = 2.0 * (config_.delta_L_m + 
                                             config_.wedge_alpha * x + 
                                             (x * x + y * y) / (2.0 * config_.R_m));

                // 2. Гаусовий профіль освітленості
                const double r_sq = x * x + y * y;
                const double w0_sq = config_.beam_radius_m * config_.beam_radius_m;
                const double gaussian = std::exp(-2.0 * r_sq / w0_sq);

                // 3. Обчислення інтенсивності
                const double phase = (M_PI * delta_s) / config_.wavelength_m;
                const double cos_val = std::cos(phase);
                const double intensity = (cos_val * cos_val) * gaussian;

                // 4. Перетворення у градацію сірого
                std::size_t char_idx = static_cast<std::size_t>(intensity * (ascii_chars.size() - 1));
                char_idx = std::clamp(char_idx, std::size_t{0}, ascii_chars.size() - 1);
                row.push_back(ascii_chars[char_idx]);
            }
            output.push_back(row);
        }
        return output;
    }

    // Збереження матриці інтенсивності у формат PGM (Netpbm Portable Graymap)
    bool exportPGM(const std::string& filename, int img_w = 512, int img_h = 512) const {
        std::ofstream outFile(filename, std::ios::binary);
        if (!outFile.is_open()) return false;

        outFile << "P5\n" << img_w << " " << img_h << "\n255\n";

        const double scale_x = 0.008 / img_w;
        const double scale_y = 0.008 / img_h;
        const double w0_sq = config_.beam_radius_m * config_.beam_radius_m;

        for (int py = 0; py < img_h; ++py) {
            const double y = (py - img_h / 2.0) * scale_y;
            for (int px = 0; px < img_w; ++px) {
                const double x = (px - img_w / 2.0) * scale_x;

                const double delta_s = 2.0 * (config_.delta_L_m + 
                                             config_.wedge_alpha * x + 
                                             (x * x + y * y) / (2.0 * config_.R_m));

                const double gaussian = std::exp(-2.0 * (x * x + y * y) / w0_sq);
                const double phase = (M_PI * delta_s) / config_.wavelength_m;
                const double cos_val = std::cos(phase);
                const double intensity = (cos_val * cos_val) * gaussian;

                unsigned char pixel_val = static_cast<unsigned char>(std::clamp(intensity * 255.0, 0.0, 255.0));
                outFile.put(static_cast<char>(pixel_val));
            }
        }
        return true;
    }

private:
    MichelsonConfig config_;
};

int main() {
    std::cout << "=== C++ Чисельне моделювання інтерферометра Майкельсона ===\n\n";

    // 1. Моделювання смуг Фізо (клин між дзеркалами)
    MichelsonConfig fizeau_cfg;
    fizeau_cfg.wedge_alpha = 25.0e-6; // 25 мкрад
    fizeau_cfg.R_m = 10.0;           // плоский хвильовий фронт

    MichelsonSimulator sim_fizeau(fizeau_cfg);
    std::cout << "--- Смуги рівної товщини (Фізо, клин alpha = 25 мкрад) ---\n";
    for (const auto& line : sim_fizeau.renderAscii()) {
        std::cout << line << "\n";
    }

    // 2. Моделювання кілець Гайдінгера (концентричні кола)
    MichelsonConfig haidinger_cfg;
    haidinger_cfg.wedge_alpha = 0.0; // паралельні дзеркала
    haidinger_cfg.R_m = 0.35;        // сферичний хвильовий фронт

    MichelsonSimulator sim_haidinger(haidinger_cfg);
    std::cout << "\n--- Смуги рівного нахилу (Гайдінгера, R = 0.35 м) ---\n";
    for (const auto& line : sim_haidinger.renderAscii()) {
        std::cout << line << "\n";
    }

    // Збереження високоякісного зображення у файл
    if (sim_fizeau.exportPGM("fizeau_pattern.pgm")) {
        std::cout << "\n[Успіх] Зображення смуг Фізо збережено у файл 'fizeau_pattern.pgm'\n";
    }

    return 0;
}
