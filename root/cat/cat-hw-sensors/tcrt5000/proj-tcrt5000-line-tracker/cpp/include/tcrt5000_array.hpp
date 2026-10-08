#ifndef TCRT5000_ARRAY_HPP
#define TCRT5000_ARRAY_HPP

#include "adc_interface.hpp"
#include <cstddef>
#include <cstdint>
#include <vector>

/**
 * @brief Структура для збереження калібрувальних екстремумів АЦП окремого давача.
 */
struct SensorCalibration {
    std::uint16_t min_value{4095}; ///< Мінімальне значення АЦП (біла поверхня)
    std::uint16_t max_value{0};    ///< Максимальне значення АЦП (чорна лінія)
};

/**
 * @brief Клас для обробки сигналів від масиву інфрачервоних давачів TCRT5000.
 * 
 * Забезпечує фільтрацію оптичних завад, динамічне калібрування екстремумів,
 * нормування вибірок АЦП до стандартизованого діапазону [0, 1000] та розрахунок
 * зсуву лінії відносно центру за допомогою алгоритму зваженого середнього.
 */
class TCRT5000Array {
public:
    /**
     * @brief Конструктор масиву TCRT5000.
     * 
     * @param adc_reader Посилання на апаратний зчитувач АЦП.
     * @param sensor_count Кількість давачів у масиві.
     * @param filter_alpha Коефіцієнт експоненційного згладжування (0.0 .. 1.0].
     */
    TCRT5000Array(IAdcArrayReader& adc_reader, std::size_t sensor_count, float filter_alpha = 0.3f);

    /**
     * @brief Скидає калібрувальні значення до початкових екстремумів.
     */
    void reset_calibration();

    /**
     * @brief Виконує один крок динамічного калібрування (оновлює min/max).
     */
    bool calibrate_step();

    /**
     * @brief Проводить повний цикл вимірювання: зчитування, фільтрація, нормування та обчислення позиції.
     * 
     * @return true У разі успішної обробки даних АЦП.
     */
    bool update();

    /**
     * @brief Повертає зсув лінії відносно центру масиву.
     * 
     * @return Відхилення від центру (негативне — ліворуч, позитивне — праворуч, 0 — у центрі).
     */
    std::int32_t get_line_error() const;

    /**
     * @brief Повертає обчислену абсолютну позицію лінії в діапазоні [0, (N-1)*1000].
     */
    std::int32_t get_line_position() const;

    /**
     * @brief Перевіряє, чи виявлена лінія під масивом давачів.
     */
    bool is_line_detected() const;

    /**
     * @brief Отримання масиву нормованих показань [0..1000].
     */
    const std::vector<std::uint16_t>& get_normalized_values() const;

    /**
     * @brief Отримання масиву відфільтрованих сирих значень АЦП.
     */
    const std::vector<std::uint16_t>& get_filtered_raw() const;

    /**
     * @brief Отримання калібрувальних параметрів усіх давачів.
     */
    const std::vector<SensorCalibration>& get_calibration() const;

private:
    IAdcArrayReader& adc_reader_;
    std::size_t sensor_count_;
    float filter_alpha_;

    std::vector<SensorCalibration> calibration_;
    std::vector<std::uint16_t> raw_buffer_;
    std::vector<std::uint16_t> filtered_raw_;
    std::vector<std::uint16_t> normalized_values_;

    std::int32_t last_position_{0};
    std::int32_t line_error_{0};
    bool line_detected_{false};
    bool first_read_{true};
};

#endif // TCRT5000_ARRAY_HPP
