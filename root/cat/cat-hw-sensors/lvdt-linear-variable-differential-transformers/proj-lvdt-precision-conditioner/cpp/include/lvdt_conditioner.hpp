#pragma once

#include "adc_interface.hpp"
#include <cstdint>

namespace lvdt {

/**
 * @brief Перелік статусів результату вимірювання LVDT.
 */
enum class Status {
    OK,            ///< Вимірювання успішне, значення в межах робочого діапазону
    Uncalibrated,  ///< Вимірювальний тракт не відкалібровано
    OutOfRange,    ///< Зсув сердечника вийшов за допустимі межі
    AdcError       ///< Помилка зчитання даних з АЦП
};

/**
 * @brief Структура параметрів двопоточкового калібрування LVDT.
 */
struct CalibrationData {
    float null_voltage_v{0.0f};        ///< Виміряна напруга АЦП у нульовому положенні (s = 0 мм)
    float ref_voltage_v{0.0f};         ///< Виміряна напруга АЦП при еталонному зсуві
    float ref_displacement_mm{0.0f};   ///< Відоме значення еталонного зсуву (мм)
    float scale_factor_k{0.0f};        ///< Обчислений масштабний коефіцієнт K (мм / В)
    bool is_calibrated{false};          ///< Прапорець придатності та дійсності калібрування
};

/**
 * @brief Результат вимірювання лінійного зсуву сердечника LVDT.
 */
struct DisplacementResult {
    float displacement_mm{0.0f};       ///< Розраховане лінійне переміщення сердечника (мм)
    float voltage_v{0.0f};             ///< Відфільтрована напруга кондиціонера (В)
    Status status{Status::Uncalibrated}; ///< Статус результату вимірювання
};

/**
 * @brief C++ клас кондиціонування сигналу та обчислення зсуву LVDT-давача.
 */
class LVDTConditioner {
public:
    /**
     * @brief Конструктор обробника сигналу LVDT.
     * @param adc_driver Посилання на драйвер АЦП (ін'єкція залежності).
     * @param min_range_mm Мінімальний допустимий робочий хід сердечника (мм).
     * @param max_range_mm Максимальний допустимий робочий хід сердечника (мм).
     * @param default_samples_count Кількість вибірок для усереднення за замовчуванням.
     */
    explicit LVDTConditioner(IAdcDriver& adc_driver,
                            float min_range_mm = -10.0f,
                            float max_range_mm = 10.0f,
                            uint16_t default_samples_count = 16);

    /**
     * @brief Ініціалізація периферії АЦП.
     * @return true у разі успішної ініціалізації АЦП.
     */
    bool init();

    /**
     * @brief Цифрове фільтрування шляхом накопичення та усереднення серії вибірок АЦП.
     * @param sample_count Кількість вибірок для усереднення.
     * @param[out] out_avg_voltage Розрахована середня напруга (В).
     * @return true при успішному зчитуванні всіх вибірок, false при помилці АЦП.
     */
    bool read_averaged_voltage(uint16_t sample_count, float& out_avg_voltage);

    /**
     * @brief Перший етап двопоточкового калібрування: фіксація нульового положення (s1 = 0 мм).
     * @param sample_count Кількість вибірок АЦП для усереднення.
     * @return true у разі успішного зчитування напруги нульової точки.
     */
    bool calibrate_null_point(uint16_t sample_count = 32);

    /**
     * @brief Другий етап двопоточкового калібрування: фіксація еталонної точки (s2 = s_ref) та розрахунок K.
     * @param ref_displacement_mm Відомий фізичний зсув еталонного блока (мм).
     * @param sample_count Кількість вибірок АЦП для усереднення.
     * @return true у разі успішного проведения калібрування та обчислення K.
     */
    bool calibrate_reference_point(float ref_displacement_mm, uint16_t sample_count = 32);

    /**
     * @brief Опитування АЦП, цифрове фільтрування та перетворення напруги у лінійний зсув.
     * @return Обчислений результат вимірювання DisplacementResult.
     */
    DisplacementResult measure_displacement();

    /**
     * @brief Встановлення збережених калібрувальних даних (наприклад, з EEPROM або Flash).
     * @param cal_data Структура CalibrationData.
     * @return true, якщо надані калібрувальні параметри є валідними.
     */
    bool set_calibration_data(const CalibrationData& cal_data);

    /**
     * @brief Отримання поточних калібрувальних даних.
     * @return Структура CalibrationData.
     */
    CalibrationData get_calibration_data() const;

    /**
     * @brief Перевірка стану калібрування вимірювального тракту.
     * @return true, якщо пристрій відкалібровано.
     */
    bool is_calibrated() const;

private:
    IAdcDriver& adc_driver_;
    CalibrationData cal_data_{};
    float min_range_mm_;
    float max_range_mm_;
    uint16_t default_samples_count_;
};

} // namespace lvdt
