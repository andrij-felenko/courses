#ifndef POWER_LOGGER_HPP
#define POWER_LOGGER_HPP

#include "ina226_driver.hpp"

namespace power_monitor {

/**
 * @brief Структура метрик для збереження поточного стану та підсумкових накопичених величин.
 */
struct PowerMetrics {
    double bus_voltage_v{0.0};   ///< Поточна напруга шини (В)
    double current_a{0.0};       ///< Поточний знаковий струм (А): >0 заряд, <0 розряд
    double power_w{0.0};         ///< Поточна миттєва потужність (Вт)
    double charge_ah{0.0};       ///< Накопичена ємність заряду (А·год)
    double discharge_ah{0.0};    ///< Накопичена ємність розряду (А·год)
    double net_ah{0.0};          ///< Результуюча чиста ємність (А·год)
    double charge_wh{0.0};       ///< Накопичена енергія заряду (Вт·год)
    double discharge_wh{0.0};    ///< Накопичена енергія розряду (Вт·год)
    double net_wh{0.0};          ///< Результуюча чиста енергія (Вт·год)
    double total_time_sec{0.0};  ///< Загальний тривалість моніторингу у секундах
    bool is_charging{false};     ///< Ознака проходження струму у напрямку заряду
};

/**
 * @brief Високорівневий C++ клас двонапрямленого логера живлення з чисельною інтеграцією.
 */
class PowerLogger {
public:
    explicit PowerLogger(Ina226Driver& driver);

    /**
     * @brief Ініціалізація логера та калібрування INA226.
     * @param r_shunt_ohms Опір вимірювального шунта (Ом).
     * @param max_expected_current_a Максимальний струм (А).
     * @return true при успішній ініціалізації.
     */
    bool init(double r_shunt_ohms, double max_expected_current_a);

    /**
     * @brief Періодичний крок опитування сенсора та чисельного інтегрування за інтервал dt_sec.
     * @param dt_sec Тривалість інтервалу часу в секундах від попереднього оновлення.
     * @return true у разі успішного зчитання даних та оновлення метрик.
     */
    bool update(double dt_sec);

    /**
     * @brief Скидання накопичених лічильників ємності (А·год) та енергії (Вт·год).
     */
    void reset_metrics();

    /**
     * @brief Перегляд поточних виміряних та накопичених метрик.
     */
    const PowerMetrics& get_metrics() const { return metrics_; }

    /**
     * @brief Переведення пристрою у сплячий режим для збереження енергії.
     */
    bool enter_sleep();

    /**
     * @brief Пробудження пристрою з відновленням регулярного моніторингу.
     */
    bool wake_up();

    /**
     * @brief Перевірка стану сну.
     */
    bool is_sleeping() const { return driver_.is_sleeping(); }

    /**
     * @brief Отримання посилання на низькорівневий драйвер.
     */
    Ina226Driver& get_driver() { return driver_; }

private:
    Ina226Driver& driver_;
    PowerMetrics metrics_{};
    bool first_sample_{true};
    double prev_current_a_{0.0};
    double prev_power_w_{0.0};
};

} // namespace power_monitor

#endif // POWER_LOGGER_HPP
