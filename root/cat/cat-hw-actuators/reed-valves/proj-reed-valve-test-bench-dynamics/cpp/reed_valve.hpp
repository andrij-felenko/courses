#ifndef REED_VALVE_HPP
#define REED_VALVE_HPP

#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>

// Клас для потокової цифрової фільтрації шумів вимірювальних сигналів стенда (ФНЧ 1-го порядку)
class SignalFilter {
private:
    double alpha_; // Коефіцієнт згладжування (0 < alpha <= 1)
    double last_value_;
    bool initialized_;

public:
    explicit SignalFilter(double cutoff_freq_ratio) 
        : alpha_(std::clamp(cutoff_freq_ratio, 0.01, 1.0)), last_value_(0.0), initialized_(false) {}

    double update(double measurement) {
        if (!initialized_) {
            last_value_ = measurement;
            initialized_ = true;
        } else {
            last_value_ = alpha_ * measurement + (1.0 - alpha_) * last_value_;
        }
        return last_value_;
    }

    void reset() {
        initialized_ = false;
        last_value_ = 0.0;
    }
};

// Клас для розрахунку інтегрального зворотного об'єму витоку та оцінки жорсткості пелюстки
class ReedValveAnalyzer {
private:
    double flow_coefficient_; // Коефіцієнт витрати через щілину клапана
    double valve_area_;       // Площа прохідного перетину пелюстки (м^2)
    double fluid_density_;    // Густина робочої рідини (кг/м^3)

public:
    ReedValveAnalyzer(double flow_coeff, double area, double density)
        : flow_coefficient_(flow_coeff), valve_area_(area), fluid_density_(density) {
        if (density <= 0.0 || area <= 0.0) {
            throw std::invalid_argument("Некоректні фізичні параметри рідини чи площі.");
        }
    }

    // Розрахунок миттєвої витрати за перепадом тиску (Па)
    double calculateInstantaneousFlow(double pressure_drop) const {
        if (pressure_drop <= 0.0) {
            return 0.0;
        }
        // Формула Бернуллі для витрати через дросельний щілинний перетин
        return flow_coefficient_ * valve_area_ * std::sqrt(2.0 * pressure_drop / fluid_density_);
    }

    // Розрахунок інтегрального зворотного об'єму витоку за масив вимірювань тиску та часовий крок (с)
    double calculateIntegralBackflow(const std::vector<double>& pressure_drops, double dt) const {
        if (dt <= 0.0) {
            throw std::invalid_argument("Часовий крок має бути додатним.");
        }
        double total_volume = 0.0;
        for (double p : pressure_drops) {
            double q = calculateInstantaneousFlow(p);
            total_volume += q * dt;
        }
        return total_volume;
    }

    // Оцінка оптимальної резонансної жорсткості пелюстки за максимальним тиском та частотою збудження
    double estimateOptimalStiffness(double max_pressure, double excitation_freq) const {
        // Спрощена модель пружної балки: k ~ (Pressure * Area) / deflection, враховуємо резонанс
        double equivalent_force = max_pressure * valve_area_;
        double target_deflection = 0.0001; // Допустимий хід пелюстки (м)
        double static_stiffness = equivalent_force / target_deflection;
        
        // Корекція на резонансну частоту (коефіцієнт динамічної жорсткості)
        double dynamic_factor = 1.0 + 0.1 * (excitation_freq / 100.0);
        return static_stiffness * dynamic_factor;
    }
};

#endif // REED_VALVE_HPP
