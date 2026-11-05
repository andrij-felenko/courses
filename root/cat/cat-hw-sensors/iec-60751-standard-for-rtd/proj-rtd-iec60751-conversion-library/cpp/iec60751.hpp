#ifndef IEC60751_HPP
#define IEC60751_HPP

#include <array>
#include <cmath>
#include <cstdint>
#include <concepts>
#include <type_traits>

namespace iec60751 {

// Строгі типи для класів допуску згідно стандарту IEC 60751
enum class ToleranceClass {
    AA,
    A,
    B,
    C
};

// Константи рівняння Каллендара-Ван Дюзена для платини (Pt)
constexpr double COEFF_A = 3.9083e-3;
constexpr double COEFF_B = -5.775e-7;
constexpr double COEFF_C = -4.183e-12;

// Обчислення допуску (максимальної похибки датчика) у градусах Цельсія
constexpr double getToleranceCelsius(ToleranceClass tClass, double temperature_c) {
    double absT = temperature_c < 0.0 ? -temperature_c : temperature_c;
    switch (tClass) {
        case ToleranceClass::AA: return 0.10 + 0.0017 * absT;
        case ToleranceClass::A:  return 0.15 + 0.0020 * absT;
        case ToleranceClass::B:  return 0.30 + 0.0050 * absT;
        case ToleranceClass::C:  return 0.60 + 0.0100 * absT;
        default: return 0.0;
    }
}

// Структура для обчислення загального бюджету похибок системи
struct ErrorBudget {
    double sensorErrorC;    // Похибка самого датчика
    double adcErrorC;       // Похибка від АЦП (приведена до градусів)
    double wireErrorC;      // Похибка від опору проводів (важливо для 2-провідних схем)
    double selfHeatingC;    // Похибка від саморозігріву вимірювальним струмом

    // Обчислення комбінованої похибки (сума квадратів)
    [[nodiscard]] double combinedError() const {
        return std::sqrt(
            sensorErrorC * sensorErrorC +
            adcErrorC * adcErrorC +
            wireErrorC * wireErrorC +
            selfHeatingC * selfHeatingC
        );
    }
};

// Шаблонний клас для генерації LUT та розрахунків
template <int R0_Ohms = 100, int MinTemp_C = -200, int MaxTemp_C = 850, int Step_C = 1>
class IEC60751Convert {
    static_assert(MinTemp_C < MaxTemp_C, "Мінімальна температура має бути меншою за максимальну");
    static_assert(Step_C > 0, "Крок має бути додатним");

public:
    static constexpr std::size_t LUT_SIZE = (MaxTemp_C - MinTemp_C) / Step_C + 1;

private:
    std::array<double, LUT_SIZE> resistance_lut{};

    // Опір при заданій температурі за стандартом
    static constexpr double calcResistance(double t) {
        if (t >= 0.0) {
            return R0_Ohms * (1.0 + COEFF_A * t + COEFF_B * t * t);
        } else {
            return R0_Ohms * (1.0 + COEFF_A * t + COEFF_B * t * t + COEFF_C * (t - 100.0) * t * t * t);
        }
    }

    // Генерація LUT під час компіляції
    constexpr void generateLUT() {
        for (std::size_t i = 0; i < LUT_SIZE; ++i) {
            double temp = MinTemp_C + static_cast<double>(i) * Step_C;
            resistance_lut[i] = calcResistance(temp);
        }
    }

public:
    constexpr IEC60751Convert() {
        generateLUT();
    }

    // Отримання температури за опором через пошук у LUT (лінійна інтерполяція)
    constexpr double temperatureFromResistance(double resistance) const {
        if (resistance <= resistance_lut.front()) return MinTemp_C;
        if (resistance >= resistance_lut.back()) return MaxTemp_C;

        // Двійковий пошук у згенерованій LUT
        std::size_t low = 0;
        std::size_t high = LUT_SIZE - 1;
        while (low < high - 1) {
            std::size_t mid = low + (high - low) / 2;
            if (resistance_lut[mid] == resistance) {
                return MinTemp_C + static_cast<double>(mid) * Step_C;
            } else if (resistance_lut[mid] < resistance) {
                low = mid;
            } else {
                high = mid;
            }
        }

        // Лінійна інтерполяція між low та high
        double rLow = resistance_lut[low];
        double rHigh = resistance_lut[high];
        double tLow = MinTemp_C + static_cast<double>(low) * Step_C;
        double tHigh = MinTemp_C + static_cast<double>(high) * Step_C;

        return tLow + (resistance - rLow) * (tHigh - tLow) / (rHigh - rLow);
    }
};

} // namespace iec60751

#endif // IEC60751_HPP
