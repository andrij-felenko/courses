#ifndef BREADBOARD_PARASITICS_ANALYZER_HPP
#define BREADBOARD_PARASITICS_ANALYZER_HPP

#include "oscilloscope_trace.hpp"

#include <string>
#include <string_view>

/**
 * @brief Оцінка технічного стану контактних затискачів макетної плати.
 */
enum class ContactHealth {
    New,         // Новий контакт (відмінний стан, R_cont < 50 мОм)
    Acceptable,  // Задовільний робочий стан (50 мОм <= R_cont <= 200 мОм)
    Degraded     // Зношений або окислений контакт (R_cont > 200 мОм)
};

/**
 * @brief Переведення технічного стану контакту в текстовий вигляд.
 */
[[nodiscard]] constexpr std::string_view contactHealthToString(ContactHealth health) noexcept {
    switch (health) {
        case ContactHealth::New:
            return "Новий (відмінний)";
        case ContactHealth::Acceptable:
            return "Задовільний";
        case ContactHealth::Degraded:
            return "Зношений / окислений";
    }
    return "Невідомий";
}

/**
 * @brief Параметри конфігурації вимірювального стенда.
 */
struct TestBenchConfig {
    double test_resistance_ohm{10000.0};  // Опір тестового резистора R_test, Ом (типово 10 кОм)
    double probe_capacitance_f{12.0e-12};  // Власна вхідна ємність щупа осцилографа C_probe, Ф (типово 12 пФ для 10X)
    double test_load_current_a{0.5};      // Тестовий струм навантаження I_test, А (типово 0.5 А)
};

/**
 * @brief Зведений метрологічний та діагностичний звіт параметрів контакту.
 */
struct ParasiticReport {
    double rise_time_ns{0.0};              // Тривалість наростання фронту t_r (10%-90%), нс
    double total_capacitance_pf{0.0};       // Повна виміряна ємність вимірювального вузла C_total, пФ
    double parasitic_capacitance_pf{0.0};   // Власна міжрейкова паразитна ємність плати C_par, пФ
    double cutoff_frequency_mhz{0.0};       // Гранична частота зрізу f_-3dB на тестовому опорі, МГц
    double voltage_drop_mv{0.0};            // Резистивне падіння напруги під струмовим навантаженням, мВ
    double contact_resistance_mohm{0.0};    // Розрахований контактний опір R_cont, мОм
    ContactHealth health{ContactHealth::New}; // Класифікація зносу контактної групи
    std::string notes;                      // Інженерний вердикт та експлуатаційні рекомендації
};

/**
 * @brief Обчислювальний аналізатор паразитних параметрів безпаяльної макетної плати.
 *
 * Виконує розрахунок міжрейкової паразитної ємності за перехідним процесом
 * заряду RC-кола з урахуванням ємності щупа, розраховує перехідний контактний опір
 * за падінням напруги під навантаженням та оцінює граничну частоту сигналів.
 */
class BreadboardParasiticsAnalyzer {
public:
    explicit BreadboardParasiticsAnalyzer(const TestBenchConfig& config = TestBenchConfig{});

    [[nodiscard]] const TestBenchConfig& config() const noexcept;
    void setConfig(const TestBenchConfig& config) noexcept;

    // Розрахунок повної ємності вузла за тривалістю наростання фронту: C_total = t_r / (ln(9) * R)
    [[nodiscard]] double calculateTotalCapacitance(double rise_time_s) const;

    // Розрахунок паразитної ємності контактів плати з компенсацією ємності щупа: C_par = C_total - C_probe
    [[nodiscard]] double calculateParasiticCapacitance(double rise_time_s) const;

    // Розрахунок контактного опору за падінням напруги: R_cont = Delta_V / I_load
    [[nodiscard]] double calculateContactResistance(double voltage_drop_v) const;

    // Розрахунок частоти зрізу f_-3dB еквівалентного RC-ланцюга для паразитної ємності плати
    [[nodiscard]] double calculateCutoffFrequency(double capacitance_f) const;

    // Автоматична класифікація технічного стану контактного затискача
    [[nodiscard]] ContactHealth assessContactHealth(double contact_resistance_ohm) const noexcept;

    // Виділення величини падіння напруги з осцилограми імпульсного навантаження
    [[nodiscard]] double extractContactVoltageDrop(const OscilloscopeTrace& load_trace) const;

    // Комплексний аналіз на основі осцилограми перехідного фронту та числового значення падіння напруги
    [[nodiscard]] ParasiticReport analyze(const OscilloscopeTrace& step_trace,
                                          double contact_voltage_drop_v) const;

    // Комплексний аналіз на основі двох осцилограм (RC-фронту та імпульсу навантаження)
    [[nodiscard]] ParasiticReport analyze(const OscilloscopeTrace& step_trace,
                                          const OscilloscopeTrace& load_trace) const;

private:
    TestBenchConfig config_;
};

#endif // BREADBOARD_PARASITICS_ANALYZER_HPP
