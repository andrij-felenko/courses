#ifndef SIR_ANALYZER_HPP
#define SIR_ANALYZER_HPP

#include <vector>
#include <string>
#include <cstdint>
#include <cstddef>

namespace flux_testing {

// Структура окремого вимірювання поверхневого опору ізоляції (SIR)
struct SirSample {
    double timestamp_hours{0.0};  // Час від початку випробування (години)
    double voltage_volts{0.0};     // Напруга тестового зміщення (В)
    double resistance_ohms{0.0};   // Виміряний поверхневий опір ізоляції (Ом)
};

// Результат виявленого локального мінімуму опору
struct LocalMinimum {
    double timestamp_hours{0.0};  // Момент часу виникнення просідання опору
    double resistance_ohms{0.0};   // Значення опору в локальному мінімумі (Ом)
    double depth_ratio{0.0};       // Відносне просідання щодо сусідніх точок (%)
};

// Підсумковий звіт чистоти та електрохімічної надійності флюсу (IPC-TM-650)
struct SirReport {
    std::string flux_name;              // Марка флюсу (наприклад, "FVS-7")
    std::size_t total_samples{0};       // Загальна кількість оброблених точок
    double initial_sir_ohms{0.0};       // Початковий опір ізоляції (Ом)
    double final_sir_ohms{0.0};         // Фінальний опір після 168 годин (Ом)
    double global_min_ohms{0.0};        // Абсолютний мінімум опору за весь тест (Ом)
    double ipc_threshold_ohms{1.0e8};   // Нормативний поріг IPC-TM-650 (100 МОм)
    bool is_ipc_compliant{false};       // Прапор відповідності нормам IPC-TM-650
    bool dendrite_growth_risk{false};   // Ризик дендритоутворення або корозії
    std::vector<LocalMinimum> local_minima; // Список виявлених локальних мінімумів
};

// Клас аналізатора часових рядів SIR-тестування
class SirTimeSeriesAnalyzer {
public:
    // Конструктор: назва флюсу та нормативний поріг IPC (за замовчуванням 10^8 Ом = 100 МОм)
    explicit SirTimeSeriesAnalyzer(std::string flux_name = "FVS-7 (No-Clean)", 
                                   double ipc_threshold_ohms = 1.0e8);

    // Додавання нового вимірювання до часового ряду
    void add_sample(const SirSample& sample);

    // Додавання масиву вимірювань
    void add_samples(const std::vector<SirSample>& samples);

    // Очищення накопичених даних
    void clear();

    // Загальна кількість накопичених вимірювань
    std::size_t sample_count() const { return raw_samples_.size(); }

    // Застосування медіанного фільтра для усунення шумових сплесків електрометра
    std::vector<SirSample> filter_median_noise(std::size_t window_size = 3) const;

    // Виявлення локальних мінімумів опору в обробленому часовому ряді
    std::vector<LocalMinimum> detect_local_minima(const std::vector<SirSample>& filtered_samples, 
                                                  double dip_threshold_pct = 15.0) const;

    // Створення підсумкового звіту електрохімічної чистоти за IPC-TM-650
    SirReport generate_report(std::size_t median_window = 3) const;

private:
    std::string flux_name_;
    double ipc_threshold_ohms_;
    std::vector<SirSample> raw_samples_;
};

} // namespace flux_testing

#endif // SIR_ANALYZER_HPP
