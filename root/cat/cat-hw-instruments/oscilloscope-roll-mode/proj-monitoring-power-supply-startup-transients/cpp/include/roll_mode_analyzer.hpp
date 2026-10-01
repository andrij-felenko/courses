#ifndef ROLL_MODE_ANALYZER_HPP
#define ROLL_MODE_ANALYZER_HPP

#include <vector>
#include <cstddef>

namespace roll_mode {

// Вибірка вимірювань осцилографа у режимі Roll Mode
struct Sample {
    double timestamp_sec; // Часова мітка відліку (секунди)
    double voltage_v;     // Напруга (вольти)
    double current_a;     // Струм (ампери)
};

// Результати аналізу стабілізації живлення
struct StabilizationResult {
    bool is_stabilized{false};
    double settling_time_sec{0.0}; // Час виходу в допускне вікно від t0
    double steady_voltage_v{0.0};  // Усталена напруга
};

// Результати аналізу розряду акумулятора
struct BatteryDischargeResult {
    double total_time_sec{0.0};    // Загальний тривалість вимірювання (секунди)
    double capacity_amp_hours{0.0};// Віддана ємність в Ампер-годинах (А·год)
    double energy_watt_hours{0.0}; // Віддана енергія у Ват-годинах (ВТ·год)
};

class RollModeAnalyzer {
public:
    explicit RollModeAnalyzer(std::vector<Sample> samples);

    // Додати нову вибірку з оновлення Roll Mode
    void addSample(const Sample& sample);

    // Отримати поточний вектор вибірок
    [[nodiscard]] const std::vector<Sample>& getSamples() const noexcept;

    // Визначення часу стабілізації напруги (settling time)
    // steady_voltage — цільова напруга, tolerance_pct — допуск (наприклад, 5.0 для 5%)
    [[nodiscard]] StabilizationResult analyzeStabilization(
        double steady_voltage,
        double tolerance_pct
    ) const;

    // Обчислення розрядної ємності акумулятора методом трапецій
    [[nodiscard]] BatteryDischargeResult calculateDischargedCapacity() const;

private:
    std::vector<Sample> m_samples;
};

} // namespace roll_mode

#endif // ROLL_MODE_ANALYZER_HPP
