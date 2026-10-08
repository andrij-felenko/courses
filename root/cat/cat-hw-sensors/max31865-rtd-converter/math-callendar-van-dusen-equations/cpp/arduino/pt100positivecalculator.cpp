#include <Arduino.h>
#include <cmath>

class Pt100PositiveCalculator {
private:
    static constexpr double R0 = 100.0;
    static constexpr double A  = 3.9083e-3;
    static constexpr double B  = -5.7750e-7;

public:
    /**
     * @brief Точне обчислення додатної температури за опором PT100
     * @param rOhms Виміряний опір у омах
     * @return Обчислена температура в °C або NAN якщо опір менший за R0
     */
    static double calculateTemperature(double rOhms) {
        if (rOhms < R0) {
            return NAN; // Для від'ємних температур потрібні чисельні методи
        }

        double rRatio = rOhms / R0;
        double absB = -B;
        double discriminant = (A * A) + (4.0 * absB * (rRatio - 1.0));

        if (discriminant < 0.0) {
            return NAN;
        }

        return (A - std::sqrt(discriminant)) / (2.0 * B);
    }
};
