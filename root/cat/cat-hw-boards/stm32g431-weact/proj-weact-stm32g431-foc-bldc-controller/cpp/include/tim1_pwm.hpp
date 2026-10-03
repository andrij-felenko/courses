#ifndef TIM1_PWM_HPP
#define TIM1_PWM_HPP

#include <cstdint>
#include <algorithm>

#if __has_include("stm32g4xx.h")
#include "stm32g4xx.h"
#else
#include <cstddef>
#endif

namespace foc {

/**
 * @brief Драйвер силового таймера TIM1 для 3-фазного інвертора.
 * Генерує комплементарні ШІМ-сигнали з мертвим часом та тригерні події для АЦП.
 */
class Tim1PwmDriver {
public:
    /**
     * @brief Конструктор драйвера TIM1.
     * @param pwm_freq_hz Частота ШІМ в Герцах (за замовчуванням 20 кГц).
     * @param dead_time_ns Мертвий час в наносекундах (за замовчуванням 1000 нс).
     */
    explicit Tim1PwmDriver(uint32_t pwm_freq_hz = 20000, uint16_t dead_time_ns = 1000);

    /**
     * @brief Ініціалізація таймера TIM1, GPIO та тригерного виходу АЦП.
     * @return true у разі успішного налаштування, false — у разі помилки.
     */
    bool init();

    /**
     * @brief Запуск генерації ШІМ та включення силового каскаду.
     */
    void start();

    /**
     * @brief Зупинка ШІМ та переведення силових виходів у безпечний стан.
     */
    void stop();

    /**
     * @brief Встановлення коефіцієнтів заповнення для трьох фаз (A, B, C).
     * @param duty_a Коефіцієнт заповнення фази A [0.0f .. 1.0f].
     * @param duty_b Коефіцієнт заповнення фази B [0.0f .. 1.0f].
     * @param duty_c Коефіцієнт заповнення фази C [0.0f .. 1.0f].
     */
    void setDutyCycles(float duty_a, float duty_b, float duty_c);

    /**
     * @brief Пряме встановлення значень регістрів порівняння CCR1, CCR2, CCR3.
     */
    void setPWMCounts(uint16_t ccr1, uint16_t ccr2, uint16_t ccr3);

    /**
     * @brief Отримання максимального значення лічильника (ARR).
     */
    uint16_t getPeriodCounts() const { return timer_period_counts_; }

    /**
     * @brief Перевірка стану ініціалізації драйвера.
     */
    bool isInitialized() const { return initialized_; }

private:
    uint32_t pwm_frequency_hz_;
    uint16_t dead_time_ns_;
    uint16_t timer_period_counts_{0};
    bool initialized_{false};

    void configureGPIO();
    void configureTimerRegisters();
    uint8_t calculateDeadTimeRegister(uint16_t dead_time_ns, uint32_t timer_clock_hz);
};

} // namespace foc

#endif // TIM1_PWM_HPP
