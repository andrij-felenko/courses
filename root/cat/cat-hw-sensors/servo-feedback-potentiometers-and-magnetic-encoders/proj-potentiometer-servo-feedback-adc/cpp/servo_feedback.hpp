#ifndef SERVO_FEEDBACK_HPP
#define SERVO_FEEDBACK_HPP

#include "ema_filter.hpp"
#include <cstdint>
#include <string_view>

/**
 * @file servo_feedback.hpp
 * @brief Інтерфейс класу давача кутового положення сервоприводу.
 */

/**
 * @brief Статус роботи давача зворотного зв'язку.
 */
enum class SensorStatus {
    Ok = 0,           ///< Відлік в межах норми
    Underflow,        ///< Відлік нижче розрахункового raw_min (можливий обрив/коротке замикання)
    Overflow,         ///< Відлік вище розрахункового raw_max (насичення АЦП/коротке замикання)
    InvalidConfig     ///< Помилка параметрів калібрування (наприклад raw_min >= raw_max)
};

/**
 * @brief Перетворення статусу давача на текстовий рядок для логування та діагностики.
 */
constexpr std::string_view status_to_string(SensorStatus status) noexcept {
    switch (status) {
        case SensorStatus::Ok:            return "OK";
        case SensorStatus::Underflow:     return "UNDERFLOW";
        case SensorStatus::Overflow:      return "OVERFLOW";
        case SensorStatus::InvalidConfig: return "INVALID_CONFIG";
        default:                          return "UNKNOWN";
    }
}

/**
 * @brief Структура збереження калібрувальних параметрів давача.
 */
struct CalibrationParams {
    uint16_t raw_min{100};        ///< Мінімальний сирий відлік АЦП
    uint16_t raw_max{3995};       ///< Максимальний сирий відлік АЦП
    float min_angle_deg{0.0f};    ///< Фізичний кут при raw_min (градуси)
    float max_angle_deg{180.0f};  ///< Фізичний кут при raw_max (градуси)
    int16_t raw_zero_offset{0};   ///< Зміщення нуля АЦП (зміщення монтажу або калібрування)

    /**
     * @brief Перевірка валідності конфігураційного набору.
     */
    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return (raw_max > raw_min) && (max_angle_deg != min_angle_deg);
    }
};

/**
 * @brief Клас обробки сигналів зворотного зв'язку кута сервоприводу.
 *
 * ІНКАПСУЛЯЦІЯ:
 * 1. Приймає сирі відліки з АЦП від потенціометра або магнітного енкодера.
 * 2. Фільтрує їх через вбудований екземпляр EmaFilter<float>.
 * 3. Перевіряє відхилення від допустимих меж.
 * 4. Застосовує калібрувальне зміщення нуля та масштабує відлік у фізичні градуси.
 */
class ServoFeedback {
public:
    /**
     * @brief Конструктор із можливістю налаштування калібрування та alpha-фільтра.
     * @param calib Структура параметрів калібрування.
     * @param filter_alpha Коефіцієнт фільтрації EMA.
     */
    explicit ServoFeedback(const CalibrationParams& calib = CalibrationParams{}, float filter_alpha = 0.2f);

    /**
     * @brief Задати нові параметри калібрування.
     * @param calib Структура параметрів.
     * @return true, якщо параметри успішно застосовані; false при помилці конфігурації.
     */
    bool set_calibration(const CalibrationParams& calib) noexcept;

    /**
     * @brief Отримати поточні параметри калібрування.
     */
    [[nodiscard]] const CalibrationParams& calibration() const noexcept;

    /**
     * @brief Ввести новий сирий відлік АЦП у контур обробки.
     * @param raw_adc Сире значення 10/12-бітного АЦП.
     * @return Поточний статус зчитування давача.
     */
    SensorStatus update_raw(uint16_t raw_adc) noexcept;

    /**
     * @brief Отримати розрахований фізичний кут у градусах.
     */
    [[nodiscard]] float angle_degrees() const noexcept;

    /**
     * @brief Отримати поточне відфільтроване значення АЦП.
     */
    [[nodiscard]] float filtered_raw() const noexcept;

    /**
     * @brief Отримати останнє невідфільтроване значення АЦП.
     */
    [[nodiscard]] uint16_t raw_adc() const noexcept;

    /**
     * @brief Отримати поточний статус давача.
     */
    [[nodiscard]] SensorStatus status() const noexcept;

    /**
     * @brief Скидання стану внутрішнього цифрового фільтра.
     */
    void reset_filter() noexcept;

    /**
     * @brief Перевірка, чи входить сирий відлік у допустимий калібрувальний діапазон.
     */
    [[nodiscard]] static bool is_in_range(uint16_t raw_adc, const CalibrationParams& calib) noexcept;

private:
    /**
     * @brief Внутрішня функція перетворення відфільтрованого АЦП у кут з урахуванням калібрування.
     */
    [[nodiscard]] float raw_to_degrees(float raw_val) const noexcept;

    CalibrationParams calib_;
    EmaFilter<float> filter_;
    uint16_t last_raw_{0};
    SensorStatus status_{SensorStatus::Ok};
};

#endif // SERVO_FEEDBACK_HPP
