#include <iostream>
#include <vector>
#include <cmath>
#include <span>
#include <expected>
#include <iomanip>
#include <algorithm>

class SensoryScaleCalculator {
public:
    struct Params {
        double i_zero{1.0e-5};   // Абсолютний поріг чутливості
        double k_weber{0.01};    // Відносний поріг Вебера
        double k_scale{10.0};    // Масштабний коефіцієнт
        double stevens_n{0.33};  // Показник степеня Стівенса
    };

    enum class Error {
        InvalidIntensity,
        InvalidWeberFraction,
        BufferTooSmall
    };

    explicit SensoryScaleCalculator(Params params) : params_(params) {}

    [[nodiscard]] double calculateFechner(double intensity) const noexcept {
        if (intensity <= params_.i_zero) {
            return 0.0;
        }
        double delta_ratio = (intensity - params_.i_zero) / params_.i_zero;
        return params_.k_scale * std::log1p(delta_ratio);
    }

    [[nodiscard]] double calculateStevens(double intensity) const noexcept {
        if (intensity <= params_.i_zero) {
            return 0.0;
        }
        return params_.k_scale * std::pow(intensity - params_.i_zero, params_.stevens_n);
    }

    [[nodiscard]] std::expected<std::vector<double>, Error> generateJndSteps(double max_intensity) const {
        if (params_.k_weber <= 0.0) {
            return std::unexpected(Error::InvalidWeberFraction);
        }
        if (max_intensity < params_.i_zero) {
            return std::unexpected(Error::InvalidIntensity);
        }

        std::vector<double> steps;
        double current_i = params_.i_zero;

        while (current_i <= max_intensity) {
            steps.push_back(current_i);
            current_i *= (1.0 + params_.k_weber);
        }

        return steps;
    }

    [[nodiscard]] static uint8_t linearToSrgb8Bit(double linear_val) noexcept {
        if (linear_val <= 0.0) return 0;
        if (linear_val >= 1.0) return 255;

        double srgb = (linear_val <= 0.0031308) 
            ? (12.92 * linear_val) 
            : (1.055 * std::pow(linear_val, 1.0 / 2.4) - 0.055);

        return static_cast<uint8_t>(std::clamp(srgb * 255.0 + 0.5, 0.0, 255.0));
    }

private:
    Params params_;
};

int main() {
    SensoryScaleCalculator::Params vision_params{
        .i_zero = 1.0e-5,
        .k_weber = 0.01,
        .k_scale = 10.0,
        .stevens_n = 0.33
    };

    SensoryScaleCalculator calc(vision_params);

    std::cout << "=== Моделювання сенсорних шкал (C++) ===\n";
    const std::vector<double> test_intensities{1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2, 1.0};

    for (double I : test_intensities) {
        double S_f = calc.calculateFechner(I);
        double S_s = calc.calculateStevens(I);
        std::cout << "I = " << std::setw(10) << std::fixed << std::setprecision(5) << I 
                  << " | S_Fechner = " << std::setw(8) << std::setprecision(4) << S_f
                  << " | S_Stevens = " << std::setw(8) << std::setprecision(4) << S_s << "\n";
    }

    auto steps_res = calc.generateJndSteps(1.0e-4);
    if (steps_res) {
        std::cout << "Згенеровано " << steps_res->size() << " JND-ступенів\n";
    }

    std::cout << "\nsRGB квантування яскравості:\n";
    const std::vector<double> luminances{0.001, 0.01, 0.1, 0.5, 1.0};
    for (double lum : luminances) {
        uint8_t px = SensoryScaleCalculator::linearToSrgb8Bit(lum);
        std::cout << "Лінійна = " << std::setw(5) << std::setprecision(3) << lum 
                  << " -> sRGB 8-bit = " << static_cast<int>(px) << "\n";
    }

    return 0;
}
