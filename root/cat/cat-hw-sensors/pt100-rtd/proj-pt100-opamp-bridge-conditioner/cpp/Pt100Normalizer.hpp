#ifndef PT100_NORMALIZER_HPP
#define PT100_NORMALIZER_HPP

#include <cstdint>
#include <optional>

/**
 * @file Pt100Normalizer.hpp
 * @brief Оголошення класу Pt100Normalizer для первинної обробки аналогового сигналу
 *        нормалізатора платинового термоопору PT100 та виконання двохточкового калібрування.
 */

/// Перелік діагностичних статусів вимірювального тракту PT100
enum class SensorStatus {
    Ok,                   ///< Сигнал у нормі, значення температури відкаліброване та дійсне
    Uncalibrated,         ///< Використовуються номінальні (некалібровані) коефіцієнти
    AdcOutOfRange,        ///< Відлік АЦП перевищує максимальну роздільну здатність
    ShortCircuit,         ///< Виявлено коротке замикання (напруга нижче мінімального порогу)
    OpenCircuit,          ///< Виявлено обрив давача (напруга вище максимального порогу)
    TemperatureOutOfRange ///< Розрахована температура виходить за межі допустимого діапазону PT100
};

/// Структура опорної калібрувальної точки (сирий відлік АЦП та еталонна температура)
struct CalibPoint {
    uint32_t raw_adc{0};        ///< Сирий відлік АЦП для еталонного стану
    float reference_temp{0.0f}; ///< Еталонне значення температури (°C)
};

/// Структура калібрувальних коефіцієнтів лінійної характеристики (T = gain * raw_adc + offset)
struct CalibCoeffs {
    float gain{0.0f};   ///< Коефіцієнт нахилу характеристики (°C / відлік АЦП)
    float offset{0.0f}; ///< Зміщення характеристики (°C)
};

/**
 * @class Pt100Normalizer
 * @brief Клас обробки аналогового сигналу нормалізатора PT100, обчислення напруги,
 *        двохточкового калібрування та перетворення відліків АЦП у температуру.
 */
class Pt100Normalizer {
public:
    /**
     * @brief Конструктор нормалізатора PT100
     * @param max_adc_count Максимальне значення АЦП (наприклад, 4095 для 12-бітного АЦП)
     * @param vref_volts Опорна напруга АЦП у Вольтах (наприклад, 3.3V)
     * @param min_expected_voltage Мінімальна припустима робоча напруга нормалізатора (В)
     * @param max_expected_voltage Максимальна припустима робоча напруга нормалізатора (В)
     */
    Pt100Normalizer(uint32_t max_adc_count,
                    float vref_volts,
                    float min_expected_voltage = 0.1f,
                    float max_expected_voltage = 3.2f);

    /**
     * @brief Перетворення сирого відліку АЦП у напругу сигналу
     * @param raw_adc Сире значення з аналогово-цифрового перетворювача
     * @return Виміряна напруга у Вольтах
     */
    [[nodiscard]] float rawToVoltage(uint32_t raw_adc) const noexcept;

    /**
     * @brief Встановлення номінального (заводського) діапазону вимірювання
     * @param temp_min Температура, що відповідає мінімальному виходу нормалізатора (0 В)
     * @param temp_max Температура, що відповідає максимальному виходу нормалізатора (Vref)
     */
    void setNominalRange(float temp_min, float temp_max) noexcept;

    /**
     * @brief Розрахунок коефіцієнтів двохточкового калібрування за двома еталонними вимірюваннями
     * @param p1 Перша еталонна точка (наприклад, 0 °C у суміші води й льоду)
     * @param p2 Друга еталонна точка (наприклад, 100 °C у киплячій воді)
     * @return true, якщо калібрування успішне; false, якщо дані некоректні
     */
    bool calibrate(const CalibPoint& p1, const CalibPoint& p2) noexcept;

    /**
     * @brief Пряме встановлення коефіцієнтів калібрування (наприклад, зчитаних із енергонезалежної пам'яті)
     * @param coeffs Нові коефіцієнти gain та offset
     * @return true, якщо коефіцієнти коректні
     */
    bool setCoefficients(const CalibCoeffs& coeffs) noexcept;

    /**
     * @brief Отримання поточних коефіцієнтів калібрування
     * @return Структура з коефіцієнтами gain та offset
     */
    [[nodiscard]] CalibCoeffs getCoefficients() const noexcept;

    /**
     * @brief Отримання статусу виконання калібрування
     * @return true, якщо об'єкт відкалібрований за двома точками
     */
    [[nodiscard]] bool isCalibrated() const noexcept { return is_calibrated_; }

    /**
     * @brief Повна обробка відліку АЦП з розрахунком температури та діагностикою тракту
     * @param raw_adc Сирий відлік АЦП
     * @param out_status Посилання на змінну для повернення детального статусу
     * @return std::optional з значенням температури у °C або std::nullopt при помилці
     */
    [[nodiscard]] std::optional<float> readTemperature(uint32_t raw_adc, SensorStatus& out_status) const noexcept;

    /**
     * @brief Спрощений метод розрахунку температури
     * @param raw_adc Сирий відлік АЦП
     * @return Фізична температура у °C або NAN при помилці тракту
     */
    [[nodiscard]] float rawToTemperature(uint32_t raw_adc) const noexcept;

    /**
     * @brief Отримання максимального значення АЦП
     */
    [[nodiscard]] uint32_t getMaxAdcCount() const noexcept { return max_adc_count_; }

    /**
     * @brief Отримання опорної напруги АЦП
     */
    [[nodiscard]] float getVref() const noexcept { return vref_volts_; }

private:
    /**
     * @brief Перевірка апаратного стану аналогового сигналу
     * @param raw_adc Сирий відлік АЦП
     * @return Результат первинної діагностики лінії
     */
    [[nodiscard]] SensorStatus checkSignalIntegrity(uint32_t raw_adc) const noexcept;

    uint32_t max_adc_count_{4095};       ///< Роздільна здатність АЦП (N_max)
    float vref_volts_{3.3f};             ///< Опорна напруга АЦП (V_ref)
    float min_expected_voltage_{0.1f};   ///< Поріг короткого замикання (В)
    float max_expected_voltage_{3.2f};   ///< Поріг обриву лінії (В)

    CalibCoeffs coeffs_{0.0f, 0.0f};     ///< Збережені коефіцієнти лінійної характеристики
    bool is_calibrated_{false};          ///< Прапор виконання двохточкового калібрування
};

#endif // PT100_NORMALIZER_HPP
