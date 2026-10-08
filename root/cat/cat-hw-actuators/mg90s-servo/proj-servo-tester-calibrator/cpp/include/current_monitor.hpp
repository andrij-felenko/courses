#ifndef CURRENT_MONITOR_HPP
#define CURRENT_MONITOR_HPP

#include <cstdint>
#include <array>
#include <cstddef>

namespace actuators {

/// @brief Налаштування аналогового вимірювача струму споживання.
struct CurrentMonitorConfig {
    uint8_t adc_pin{0};                         // АЦП-канал для зчитування напруги струмового сенсора
    float ref_voltage_v{3.3f};                  // Опорна напруга АЦП (у вольтах)
    uint16_t adc_resolution_bits{12};           // Розрядність АЦП (12 біт = 4096 відліків)
    float sensor_sensitivity_mv_per_ma{0.185f}; // Чутливість датчика струму (0.185 мВ/мА для ACS712-05B)
    float zero_offset_v{1.65f};                 // Напруга нульового струму (VCC / 2)
    float stall_threshold_ma{650.0f};           // Поріг струму заклинювання редуктора (мА)
    uint8_t stall_confirm_samples{4};           // Кількість послідовних вибірок для підтвердження заклинювання
};

/// @brief Клас моніторингу струму споживання сервопривода із цифровим фільтром та захистом від перевантаження.
class CurrentMonitor {
public:
    static constexpr size_t FILTER_WINDOW_SIZE = 8; // Розмір вікна ковзного середнього

    explicit CurrentMonitor(const CurrentMonitorConfig& config = CurrentMonitorConfig{});

    /// @brief Ініціалізація АЦП та обнулення фільтруючих буферів.
    void initialize();

    /// @brief Обробка нового сирого вимірювання АЦП.
    /// @param raw_adc Сире значення відліку АЦП (0..(2^bits - 1)).
    /// @return Відфільтроване значення струму у міліамперах.
    float process_sample(uint16_t raw_adc);

    /// @brief Введення прямого значення струму у міліамперах (для симуляції та тестів).
    /// @param current_ma Струм у мА.
    /// @return Відфільтроване значення струму.
    float process_direct_ma(float current_ma);

    /// @brief Перетворення сирого відліку АЦП у напругу на вході.
    float get_raw_adc_voltage(uint16_t raw_adc) const;

    /// @brief Перетворення сирого відліку АЦП у струм (мА).
    float raw_adc_to_ma(uint16_t raw_adc) const;

    /// @brief Отримання поточного відфільтрованого струму споживання (мА).
    float get_filtered_current_ma() const;

    /// @brief Отримання пікового виміряного струму (мА).
    float get_peak_current_ma() const;

    /// @brief Перевірка прапорця аварійного заклинювання сервопривода.
    bool is_stall_detected() const;

    /// @brief Зміна граничного порогу струму заклинювання.
    void set_stall_threshold_ma(float ma);

    /// @brief Скидання аварійного прапорця заклинювання.
    void reset_stall_alarm();

    /// @brief Скидання статистики пікових значень струму.
    void reset_statistics();

private:
    CurrentMonitorConfig config_;
    std::array<float, FILTER_WINDOW_SIZE> sample_buffer_{};
    size_t buffer_index_{0};
    size_t sample_count_{0};
    float filtered_current_ma_{0.0f};
    float peak_current_ma_{0.0f};
    uint8_t overcurrent_counter_{0};
    bool stall_flag_{false};

    void update_moving_average(float new_ma);
    void check_stall_condition();
};

} // namespace actuators

#endif // CURRENT_MONITOR_HPP
