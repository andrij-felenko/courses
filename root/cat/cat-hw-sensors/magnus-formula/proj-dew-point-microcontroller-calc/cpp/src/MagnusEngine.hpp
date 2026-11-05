#pragma once

#include <cmath>

// Виконує чисті математичні обчислення точки роси за формулою Магнуса-Тетенса.
class MagnusEngine {
public:
    // Коефіцієнти формули (за замовчуванням константи Альдухава-Ескріджа / Соннтага).
    struct Coefficients {
        float b;
        float c;
    };

    explicit MagnusEngine(Coefficients coeffs = {17.62f, 243.12f}) : coeffs_(coeffs) {}

    // Повертає точку роси в °C.
    // temperature: поточна температура (°C)
    // humidity: відносна вологість (%)
    [[nodiscard]] float calculateDewPoint(float temperature, float humidity) const {
        if (humidity <= 0.0f) {
            return -273.15f; // Уникнення логарифма нуля/від'ємних значень
        }

        // Обмежуємо вологість (100% — максимум у природі)
        if (humidity > 100.0f) {
            humidity = 100.0f;
        }

        // Формула:
        // gamma(T, RH) = ln(RH / 100) + (b * T) / (c + T)
        // T_dp = (c * gamma) / (b - gamma)
        const float gamma = std::log(humidity / 100.0f) + 
                            (coeffs_.b * temperature) / (coeffs_.c + temperature);

        return (coeffs_.c * gamma) / (coeffs_.b - gamma);
    }

private:
    Coefficients coeffs_;
};
