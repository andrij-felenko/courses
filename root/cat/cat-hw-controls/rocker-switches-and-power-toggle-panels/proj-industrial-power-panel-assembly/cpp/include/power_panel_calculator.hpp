#ifndef POWER_PANEL_CALCULATOR_HPP
#define POWER_PANEL_CALCULATOR_HPP

#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

/**
 * @file power_panel_calculator.hpp
 * @brief Класи розрахунку електричного опору, спаду напруги, перерізу жил та теплового балансу рокерних панелей.
 */

namespace PowerPanel {

/**
 * @brief Питомий опір міді за 20 °C (Ом·мм²/м).
 */
constexpr double COPPER_RESISTIVITY = 0.0175;

/**
 * @brief Стандартний ряд перерізів мідних жил електричних кабелів (мм²).
 */
inline const std::vector<double> STANDARD_WIRE_SECTIONS = {
    0.5, 0.75, 1.0, 1.5, 2.5, 4.0, 6.0, 10.0, 16.0, 25.0
};

/**
 * @brief Контейнер конфігураційних параметрів силового кола.
 */
struct PowerCircuitConfig {
    double voltageV{230.0};                     ///< Робоча напруга кола (В)
    double currentA{10.0};                      ///< Струм навантаження (А)
    double wireLengthM{10.0};                   ///< Сумарна довжина провідника силової лінії (м)
    double wireSectionMm2{1.5};                 ///< Поточний переріз провідника (мм²)
    double wireResistivityOhmMm2M{COPPER_RESISTIVITY}; ///< Питомий опір провідника (Ом·мм²/м)
    double switchContactResistanceMohm{20.0};  ///< Опір контактної групи перемикача (мОм)
    double switchThermalResistanceCw{20.0};    ///< Тепловий опір корпус-довкілля R_th (°C/Вт)
    double ambientTempC{25.0};                  ///< Температура навколишнього середовища (°C)
    double maxAllowedTempC{85.0};               ///< Максимально допустима температура корпусу (°C)
    double maxAllowedVoltageDropPercent{3.0};  ///< Максимально допустимий спад напруги (%)
};

/**
 * @brief Результати обчислення електричних втрат та теплового режиму панелі.
 */
struct CalculationResult {
    double wireResistanceOhm{0.0};      ///< Опір провідників лінії (Ом)
    double voltageDropV{0.0};           ///< Падіння напруги на лінії (В)
    double voltageDropPercent{0.0};     ///< Відносне падіння напруги (%)
    double wirePowerLossW{0.0};         ///< Теплові втрати у провіднику (Вт)
    double contactPowerLossW{0.0};      ///< Втрати потужності на контактах рокера (Вт)
    double temperatureRiseC{0.0};       ///< Перегрів корпусу відносно довкілля (°C)
    double finalTemperatureC{0.0};      ///< Підсумкова стаціонарна температура корпусу (°C)
    double currentDensityAMm2{0.0};     ///< Фактична густина струму в провіднику (А/мм²)
    double recommendedSectionMm2{0.0};  ///< Мінімально необхідний переріз із стандартного ряду (мм²)
    bool isVoltageDropSafe{false};      ///< Безпека за спадом напруги
    bool isThermalSafe{false};          ///< Безпека за температурою корпусу
    bool isCurrentDensitySafe{false};   ///< Безпека за густиною струму
    bool isOverallSafe{false};          ///< Загальний висновок про безпеку експлуатації
};

/**
 * @brief Клас розрахунку електричного та теплового балансу силових комутаційних панелей.
 */
class PowerPanelCalculator {
public:
    /**
     * @brief Конструктор із передачею конфігурації симуляції.
     */
    explicit PowerPanelCalculator(PowerCircuitConfig config);

    /**
     * @brief Оновлення конфігурації силового кола.
     */
    void setConfig(const PowerCircuitConfig& config);

    /**
     * @brief Отримання поточної конфігурації.
     */
    [[nodiscard]] const PowerCircuitConfig& getConfig() const;

    /**
     * @brief Обчислення електричного опору провідника лінії.
     */
    [[nodiscard]] double calculateWireResistance() const;

    /**
     * @brief Обчислення падіння напруги на лінії.
     */
    [[nodiscard]] double calculateVoltageDrop() const;

    /**
     * @brief Обчислення теплових втрат на контактах перемикача.
     */
    [[nodiscard]] double calculateContactPowerLoss() const;

    /**
     * @brief Розрахунок стаціонарного підйому температури корпусу (Delta T).
     */
    [[nodiscard]] double calculateTemperatureRise() const;

    /**
     * @brief Підбір мінімального рекомендованого перерізу провідника за допустимою густиною струму та спадом напруги.
     * @param maxCurrentDensity Максимально допустима густина струму (А/мм², за замовчуванням 5.0).
     */
    [[nodiscard]] double findRecommendedWireSection(double maxCurrentDensity = 5.0) const;

    /**
     * @brief Комплексний аналіз силового кола та формування результату.
     */
    [[nodiscard]] CalculationResult analyze() const;

    /**
     * @brief Друк інженерного звіту діагностики силової панелі у консоль.
     */
    void printReport(const CalculationResult& result) const;

private:
    PowerCircuitConfig m_config;
};

} // namespace PowerPanel

#endif // POWER_PANEL_CALCULATOR_HPP
