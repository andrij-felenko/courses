#ifndef ATTENUATOR_CALCULATOR_HPP
#define ATTENUATOR_CALCULATOR_HPP

#include <vector>
#include <string>
#include <array>

// Енумерація рядів стандартних опорів резисторів
enum class ResistorSeries {
    E24,
    E96
};

// Перелічення типів шкали атенюації
enum class AttenuationScale {
    Logarithmic, // Логарифмічна (в децибелах, для регулювань гучності)
    Linear       // Лінійна (лінійні коефіцієнти передачі)
};

// Структура даних для збереження параметрів окремого ступеня атенюатора
struct AttenuatorStep {
    size_t position;           // Номер позиції галетного перемикача (1..N)
    double target_attenuation_db; // Цільове ослаблення у дБ
    double target_voltage_ratio; // Цільовий коефіцієнт передачі напруги (0.0 .. 1.0)
    
    double r_series_ideal;     // Теоретичний послідовний опір (Ом)
    double r_shunt_ideal;      // Теоретичний паралельний опір (Ом)
    
    double r_series_e24;       // Обраний послідовний опір із ряду E24 (Ом)
    double r_series_e96;       // Обраний послідовний опір із ряду E96 (Ом)
    
    double r_shunt_e24;        // Обраний паралельний опір із ряду E24 (Ом)
    double r_shunt_e96;        // Обраний паралельний опір із ряду E96 (Ом)
    
    double actual_attenuation_db_e24; // Фактичне ослаблення з резисторами E24 (дБ)
    double actual_attenuation_db_e96; // Фактичне ослаблення з резисторами E96 (дБ)
    
    double error_db_e24;       // Абсолютна похибка ослаблення E24 (дБ)
    double error_db_e96;       // Абсолютна похибка ослаблення E96 (дБ)
    
    double power_dissipation_series_mw; // Максимальна розсіювана потужність на послідовному резисторі (мВт)
    double power_dissipation_shunt_mw;  // Максимальна розсіювана потужність на паралельному резисторі (мВт)
};

// Клас AttenuatorCalculator реалізує розрахунок резистивної матриці галетного перемикача
class AttenuatorCalculator {
public:
    // Конструктор калькулятора атенюатора
    // positions: кількість позицій перемикача
    // input_impedance_ohm: цільовий вхідний опір дільника (Ом)
    // max_attenuation_db: максимальне ослаблення у дБ для останньої позиції
    AttenuatorCalculator(size_t positions, double input_impedance_ohm, double max_attenuation_db);

    // Виконати обчислення теоретичних опорів та апроксимації рядами E24/E96
    void calculate(AttenuationScale scale = AttenuationScale::Logarithmic);

    // Отримати результати розрахунку для всіх ступенів
    const std::vector<AttenuatorStep>& get_steps() const;

    // Знайти найближчий стандартний номінал резистора з вказаного ряду
    static double find_closest_resistor(double target_value_ohm, ResistorSeries series);

    // Таблиці баз стандартних рядів E24 та E96
    static const std::array<double, 24> E24_BASE_VALUES;
    static const std::array<double, 96> E96_BASE_VALUES;

private:
    size_t num_positions_;
    double input_impedance_;
    double max_attenuation_db_;
    std::vector<AttenuatorStep> steps_;
};

#endif // ATTENUATOR_CALCULATOR_HPP
