#ifndef PI_CONTROLLER_HPP
#define PI_CONTROLLER_HPP

#include <algorithm>

namespace foc {

/**
 * @brief Дискретний ПІ-регулятор із підтримкою обмеження виходу та Anti-Windup.
 */
class PiController {
public:
    /**
     * @brief Конструктор ПІ-регулятора.
     * @param kp Пропорційний коефіцієнт.
     * @param ki Інтегральний коефіцієнт.
     * @param dt Період квантування у секундах (наприклад, 50 мкс = 0.00005s).
     * @param out_min Мінімальне значення виходу.
     * @param out_max Максимальне значення виходу.
     */
    PiController(float kp = 0.0f, float ki = 0.0f, float dt = 0.00005f,
                 float out_min = -1.0f, float out_max = 1.0f);

    /**
     * @brief Встановлення коефіцієнтів підсилення P та I.
     */
    void setGains(float kp, float ki);

    /**
     * @brief Встановлення меж обмеження вихідного сигналу регулятора.
     */
    void setOutputLimits(float out_min, float out_max);

    /**
     * @brief Скинути накопичений інтегратор та попередню помилку.
     */
    void reset();

    /**
     * @brief Розрахунок нового значення керуючого впливу за поточним кроком дискретизації.
     * @param setpoint Задане значення (Ref).
     * @param measured Фактично виміряне значення (Feedback).
     * @return Керуючий вплив із врахуванням сатурації.
     */
    float update(float setpoint, float measured);

    /**
     * @brief Отримання поточного значення інтегральної суми.
     */
    float getIntegral() const { return integral_; }

private:
    float kp_;
    float ki_;
    float dt_;
    float out_min_;
    float out_max_;
    float integral_{0.0f};
    float prev_error_{0.0f};
};

} // namespace foc

#endif // PI_CONTROLLER_HPP
