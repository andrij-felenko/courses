#ifndef PYROMETER_HPP
#define PYROMETER_HPP

#include <string>
#include <vector>
#include <optional>
#include <cmath>

namespace pyrometer {

// Фізична константа переведення температури в Кельвіни
constexpr double KELVIN_OFFSET = 273.15;

/**
 * @brief Перелічувальний тип статусів теплового стану компонента
 */
enum class ThermalStatus {
    Safe,             // Температура в межах норми
    Warning,          // Температура наближається до максимально припустимої межі
    CriticalOverheat, // Перевищено максимально припустиму температуру
    InvalidReading    // Похибка вимірювання (некоректні вхідні дані)
};

/**
 * @brief Результат оцінки теплового допуску компонента
 */
struct ThermalEvaluationResult {
    std::string componentName;    // Назва компонента
    double measuredTempCelsius;   // Виміряна температура (°C)
    double maxAllowedTempCelsius; // Максимально припустима температура (°C)
    double thermalMarginCelsius;  // Залишковий температурний запас (°C)
    ThermalStatus status;         // Статус теплового стану
};

/**
 * @brief Клас обробки вимірювальних даних інфрачервоного пірометра MESTEK IR01B
 */
class PyrometerSensor {
public:
    /**
     * @param sensitivityCoeff Коефіцієнт чутливості термостовпчика
     */
    explicit PyrometerSensor(double sensitivityCoeff = 1.2e-11);

    /**
     * @brief Налаштувати коефіцієнт випромінювальної здатності поверхні ε
     * @param emissivity Значення від 0.10 до 1.00
     * @return true, якщо значення валідне
     */
    bool setEmissivity(double emissivity);

    /**
     * @brief Отримати поточний коефіцієнт емісивності ε
     */
    [[nodiscard]] double getEmissivity() const noexcept;

    /**
     * @brief Обчислити дійсну температуру об'єкта за напругою термостовпчика
     * @param sensorVoltageVolt Напруга з виходу ІЧ-сенсора в вольтах (В)
     * @param backgroundTempCelsius Фонова відбита температура навколишнього середовища (°C)
     * @return Температура об'єкта в °C або std::nullopt у разі фізично неможливих даних
     */
    [[nodiscard]] std::optional<double> calculateTargetTemperature(
        double sensorVoltageVolt, 
        double backgroundTempCelsius) const;

private:
    double emissivity_{0.95};
    double sensitivityCoeff_;
};

/**
 * @brief Клас контролю та оцінки температурних допусків компонентів
 */
class ThermalToleranceEvaluator {
public:
    /**
     * @param warningMarginCelsius Запас у °C для подачі попередження про перегрів
     */
    explicit ThermalToleranceEvaluator(double warningMarginCelsius = 15.0);

    /**
     * @brief Оцінити тепловий стан компонента
     * @param componentName Назва об'єкта
     * @param measuredTempCelsius Виміряна температура (°C)
     * @param maxAllowedTempCelsius Максимально припустима робоча температура (°C)
     * @return Структура з даними оцінки теплового запасу та статусом
     */
    [[nodiscard]] ThermalEvaluationResult evaluate(
        const std::string& componentName,
        double measuredTempCelsius,
        double maxAllowedTempCelsius) const;

private:
    double warningMargin_;
};

} // namespace pyrometer

#endif // PYROMETER_HPP
