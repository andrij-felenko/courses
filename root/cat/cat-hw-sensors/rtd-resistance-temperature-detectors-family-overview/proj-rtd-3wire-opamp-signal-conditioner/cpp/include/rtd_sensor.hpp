#ifndef RTD_SENSOR_HPP
#define RTD_SENSOR_HPP

#include <cstdint>
#include <string_view>
#include "callendar_van_dusen.hpp"

namespace sensors::rtd {

/**
 * @brief Структура конфігураційних параметрів АЦП.
 */
struct AdcConfig {
    double vref_volts{3.3};          ///< Опорна напруга АЦП (Вольт)
    double gain{1.0};                ///< Коефіцієнт підсилення вхідного підсилювача (PGA)
    uint8_t resolution_bits{16};     ///< Розрядність АЦП (біти)
    bool is_ratiometric{true};       ///< Прапорець співвідносного (ratiometric) зчитування
    double r_ref_ohms{400.0};        ///< Опір еталонного резистора (Ом) для співвідносного режиму
    double i_bias_amps{0.001};       ///< Струм збудження (Ампер) для абсолютного режиму

    /**
     * @brief Максимальний код АЦП для заданої розрядності.
     */
    [[nodiscard]] double getMaxCode() const {
        return static_cast<double>((1ULL << resolution_bits) - 1ULL);
    }
};

/**
 * @brief Структура параметрів двоточкового калібрування вимірювального тракту.
 */
struct CalibrationParams {
    double offset_ohms{0.0};    ///< Системний зсув нуля (Ом)
    double scale_factor{1.0};   ///< Масштабний коефіцієнт корекції (безрозмірний)

    /**
     * @brief Розрахунок коефіцієнтів двоточкового калібрування за еталонними опорами.
     * @param r_std1 Перший еталонний опір (Ом)
     * @param r_meas1 Виміряний сирий опір першої точки (Ом)
     * @param r_std2 Другий еталонний опір (Ом)
     * @param r_meas2 Виміряний сирий опір другої точки (Ом)
     * @return true у разі успішного обчислення, false при діленні на нуль.
     */
    bool calibrateTwoPoint(double r_std1, double r_meas1, double r_std2, double r_meas2);

    /**
     * @brief Застосування калібрування до виміряного значення опору.
     */
    [[nodiscard]] double apply(double r_raw) const {
        return (r_raw * scale_factor) + offset_ohms;
    }
};

/**
 * @brief Перелічення можливих статусів вимірювального тракту та діагностичних подій.
 */
enum class SensorStatus : uint8_t {
    Ok,               ///< Нормальна робота, вимірювання валідне
    Underflow,        ///< Температура нижча за мінімально припустиму межу
    Overflow,         ///< Температура вища за максимально припустиму межу
    OpenCircuit,      ///< Фіксація обриву кола датчика (High Resistance)
    ShortCircuit,     ///< Фіксація короткого замикання (Low Resistance)
    InvalidAdcCode,   ///< Отримано код АЦП поза діапазоном розрядності
    CalibrationError  ///< Некоректні коефіцієнти калібрування
};

/**
 * @brief Текстове представлення статусу вимірювання.
 */
[[nodiscard]] std::string_view statusToString(SensorStatus status);

/**
 * @brief Повний результат первинної обробки оцифрованого сигналу RTD.
 */
struct MeasurementResult {
    double temperature_c{0.0};         ///< Обчислена температура (°C)
    double resistance_raw_ohms{0.0};   ///< Некалібрований опір (Ом)
    double resistance_cal_ohms{0.0};   ///< Відкалібрований опір (Ом)
    double voltage_volts{0.0};         ///< Обчислена напруга на вході АЦП (В)
    SensorStatus status{SensorStatus::Ok}; ///< Статус діагностики

    [[nodiscard]] bool isValid() const { return status == SensorStatus::Ok; }
};

/**
 * @brief Головний C++ драйвер вимірювального тракту терморезистора RTD.
 */
class RtdSensor {
public:
    RtdSensor(const AdcConfig& adc_config,
              RtdType rtd_type = RtdType::Pt100,
              const CalibrationParams& cal_params = CalibrationParams{},
              double min_temp_c = -200.0,
              double max_temp_c = 850.0);

    /**
     * @brief Головна функція обробки коду АЦП та розрахунку температури.
     * @param adc_code Оцифроване значення з АЦП.
     * @return Заповнена структура MeasurementResult з результатами та діагностикою.
     */
    [[nodiscard]] MeasurementResult processAdcCode(int32_t adc_code) const;

    /**
     * @brief Перетворення коду АЦП у первинний (сирий) опір датчика.
     */
    [[nodiscard]] double adcCodeToRawResistance(int32_t adc_code) const;

    /**
     * @brief Перетворення коду АЦП у вхідну напругу (В).
     */
    [[nodiscard]] double adcCodeToVoltage(int32_t adc_code) const;

    /**
     * @brief Двоточкове калібрування тракту за еталонними опорами та кодами АЦП.
     */
    bool calibrateTwoPoint(double r_std1, int32_t adc_code1, double r_std2, int32_t adc_code2);

    // Управління конфігурацією та межами
    void setAdcConfig(const AdcConfig& config);
    [[nodiscard]] const AdcConfig& getAdcConfig() const { return adc_config_; }

    void setCalibrationParams(const CalibrationParams& params);
    [[nodiscard]] const CalibrationParams& getCalibrationParams() const { return cal_params_; }

    void setTemperatureLimits(double min_c, double max_c);
    [[nodiscard]] double getMinTemperature() const { return min_temp_c_; }
    [[nodiscard]] double getMaxTemperature() const { return max_temp_c_; }

    [[nodiscard]] const CallendarVanDusen& getSolver() const { return solver_; }

private:
    AdcConfig adc_config_;
    CalibrationParams cal_params_;
    CallendarVanDusen solver_;
    double min_temp_c_{-200.0};
    double max_temp_c_{850.0};
    double min_resistance_ohms_{18.5};
    double max_resistance_ohms_{390.5};

    void updateResistanceLimits();
};

} // namespace sensors::rtd

#endif // RTD_SENSOR_HPP
