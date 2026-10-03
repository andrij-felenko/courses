#ifndef FOC_CONTROLLER_HPP
#define FOC_CONTROLLER_HPP

#include "tim1_pwm.hpp"
#include "adc_opamp.hpp"
#include "cordic_math.hpp"
#include "pi_controller.hpp"

namespace foc {

/**
 * @brief Стани роботи FOC-контролера.
 */
enum class ControlState {
    STOPPED,
    CALIBRATING,
    RUNNING,
    ERROR
};

/**
 * @brief Головний координатор системи векторного керування (FOC Controller).
 * Об'єднує силову периферію, аналоговий тракт, CORDIC та каскад ПІ-регуляторів.
 */
class FOCController {
public:
    /**
     * @brief Конструктор FOC-контролера.
     * @param pwm Посилання на драйвер силового ШІМ.
     * @param adc Посилання на драйвер аналогового тракту (АЦП/OPAMP).
     */
    FOCController(Tim1PwmDriver& pwm, AdcOpampDriver& adc);

    /**
     * @brief Початкова конфігурація периферії та підсистем.
     * @return true у разі успішного налаштування.
     */
    bool init();

    /**
     * @brief Запуск процедури калібрування та виконання FOC у реальному часі.
     */
    void start();

    /**
     * @brief Безумовна зупинка інвертора та FOC-обчислень.
     */
    void stop();

    /**
     * @brief Встановлення узагальнених уставильних струмів по осях d та q.
     * @param id_ref Заданий струм поздовжньої осі d (Ампери).
     * @param iq_ref Заданий струм поперечної осі q (Ампери).
     */
    void setTargetCurrents(float id_ref, float iq_ref);

    /**
     * @brief Оновлення електричного кута ротора (наприклад, від енкодера чи спостерігача).
     * @param angle_rad Кут у радіанах.
     */
    void setElectricalAngle(float angle_rad);

    /**
     * @brief Метод, що викликається з обробника переривання АЦП (ADC ISR) на кожному такті ШІМ.
     */
    void updateInterruptHandler();

    /**
     * @brief Отримання поточного стану FOC-системи.
     */
    ControlState getState() const { return state_; }

    /**
     * @brief Отримання виміряного струму осі d.
     */
    float getMeasuredId() const { return measured_id_; }

    /**
     * @brief Отримання виміряного струму осі q.
     */
    float getMeasuredIq() const { return measured_iq_; }

private:
    Tim1PwmDriver& pwm_driver_;
    AdcOpampDriver& adc_driver_;
    CordicMath cordic_math_;

    PiController pi_d_;
    PiController pi_q_;

    ControlState state_{ControlState::STOPPED};

    float target_id_{0.0f};
    float target_iq_{0.0f};

    float measured_id_{0.0f};
    float measured_iq_{0.0f};

    float electrical_angle_rad_{0.0f};
    float bus_voltage_v_{24.0f};
};

} // namespace foc

#endif // FOC_CONTROLLER_HPP
