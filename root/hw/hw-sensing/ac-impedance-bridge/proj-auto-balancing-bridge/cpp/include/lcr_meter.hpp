#ifndef LCR_METER_HPP
#define LCR_METER_HPP

#include <complex>
#include <string>
#include <cmath>

/**
 * @brief Результат вимірювання еквівалентних параметрів двополюсника.
 */
struct MeasurementResult {
    std::complex<double> z_raw;       ///< Сирий виміряний імпеданс, Ом
    std::complex<double> z_corrected; ///< Скомпенсований імпеданс після Open/Short, Ом
    
    double r_series;    ///< Послідовний активний опір (Rs), Ом
    double x_series;    ///< Послідовний реактивний опір (Xs), Ом
    double c_series;    ///< Послідовна еквівалентна ємність (Cs), Ф (якщо Xs < 0)
    double l_series;    ///< Послідовна еквівалентна індуктивність (Ls), Гн (якщо Xs > 0)
    
    double r_parallel;  ///< Паралельний активний опір (Rp), Ом
    double c_parallel;  ///< Паралельна еквівалентна ємність (Cp), Ф
    double l_parallel;  ///< Паралельна еквівалентна індуктивність (Lp), Гн
    
    double quality_factor;     ///< Добротність Q = |Xs| / Rs
    double dissipation_factor; ///< Тангенс кута втрат D = 1 / Q = Rs / |Xs|
    double phase_deg;          ///< Фазовий кут імпедансу, градуси
};

/**
 * @brief Клас вимірювача LCR із функцією корекції паразитних опорів і ємностей щупів.
 */
class LCRMeter {
public:
    /**
     * @brief Конструктор із зазначенням робочої частоти.
     * @param test_frequency_hz Частота синусоїдального сигналу збудження, Гц.
     */
    explicit LCRMeter(double test_frequency_hz);

    /**
     * @brief Встановлення нової робочої частоти вимірювання.
     */
    void set_frequency(double test_frequency_hz);
    double get_frequency() const noexcept { return frequency_hz_; }

    /**
     * @brief Калібрування холостого ходу (Open Compensation).
     * @param z_open_raw Виміряний імпеданс розімкнених щупів.
     */
    void calibrate_open(const std::complex<double>& z_open_raw);

    /**
     * @brief Калібрування короткого замикання (Short Compensation).
     * @param z_short_raw Виміряний імпеданс замкнених щупів.
     */
    void calibrate_short(const std::complex<double>& z_short_raw);

    /**
     * @brief Скидання калібрувальних коефіцієнтів до ідеальних (Y_open = 0, Z_short = 0).
     */
    void reset_calibration() noexcept;

    /**
     * @brief Виконання вимірювання та обчислення параметрів компонента.
     * @param z_raw Сирий виміряний імпеданс на клемах приладу.
     * @return Повна структура розрахованих фізичних параметрів зразка.
     */
    MeasurementResult measure(const std::complex<double>& z_raw) const;

private:
    double frequency_hz_;
    double omega_; // 2 * pi * f

    std::complex<double> z_short_{0.0, 0.0}; ///< Паразитний послідовний імпеданс контактів
    std::complex<double> y_open_{0.0, 0.0};  ///< Паразитна паралельна провідність щупів
    bool has_open_cal_{false};
    bool has_short_cal_{false};
};

#endif // LCR_METER_HPP
