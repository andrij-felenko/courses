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
 * @brief Клас для обробки сигналів масиву оптичних ІЧ-давачів TCRT5000.
 * 
 * Реалізує ЕМА-фільтрацію фонового засвічення, динамічне калібрування,
 * нормування вибірок до діапазону [0, 1000] та розрахунок відхилення лінії.
 */
class TCRT5000Array {
public:
    /**
     * @brief Конструктор масиву TCRT5000.
     * 
     * @param adc_reader Посилання на апаратний інтерфейс АЦП.
     * @param sensor_count Кількість давачів у масиві.
     * @param filter_alpha Коефіцієнт експоненційного згладжування (0.0 < alpha <= 1.0).
     */
    TCRT5000Array(IAdcArrayReader& adc_reader, std::size_t sensor_count, float filter_alpha = 0.3f);

    /**
     * @brief Скидає калібрувальні межі давачів до вихідних екстремумів.
     */
    void reset_calibration();

    /**
     * @brief Виконує один крок динамічного калібрування (фіксує min/max).
     * 
     * @return true у разі успішного зчитування даних для калібрування.
     */
    bool calibrate_step();

    /**
     * @brief Оновлює стан масиву: зчитування, EMA-фільтрація, нормування та зважене середнє.
     * 
     * @return true у разі успішного оновлення вибірок.
     */
    bool update();

    /**
     * @brief Повертає зсув лінії відносно центральної осі масиву.
     * 
     * @return Помилка відхилення (від'ємне — вліво, додатне — вправо, 0 — в центрі).
     */
    std::int32_t get_line_error() const;

    /**
     * @brief Повертає обчислену абсолютну позицію лінії в діапазоні [0, (N-1)*1000].
     */
    std::int32_t get_line_position() const;

    /**
     * @brief Перевіряє, чи виявлена чорна лінія під масивом.
     */
    bool is_line_detected() const;

    /**
     * @brief Повертає вектор нормованих показань [0, 1000].
     */
    const std::vector<std::uint16_t>& get_normalized_values() const;

    /**
     * @brief Повертає вектор відфільтрованих сирих значень АЦП.
     */
    const std::vector<std::uint16_t>& get_filtered_raw() const;

    /**
     * @brief Повертає вектор параметрів калібрування для всіх давачів.
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
