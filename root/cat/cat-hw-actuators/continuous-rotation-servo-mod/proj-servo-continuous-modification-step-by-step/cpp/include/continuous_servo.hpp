#ifndef CONTINUOUS_SERVO_HPP
#define CONTINUOUS_SERVO_HPP

#include <cstdint>
#include "pwm_timer.hpp"

/**
 * @brief Напрямок обертання вала сервопривода постійного обертання.
 */
enum class ServoDirection : int8_t {
    CounterClockwise = -1, /// Проти годинникової стрілки (CCW)
    Stop = 0,             /// Повна зупинка вала
    Clockwise = 1         /// За годинниковою стрілкою (CW)
};

/**
 * @brief Структура конфігурації тривалості ШІМ-імпульсів для сервопривода.
 */
struct ServoPwmConfig {
    uint16_t min_pulse_us{1000};     /// Імпульс максимальної швидкості CCW (-100%)
    uint16_t neutral_pulse_us{1500}; /// Базова нейтральна точка зупинки (0%)
    uint16_t max_pulse_us{2000};     /// Імпульс максимальної швидкості CW (+100%)
    int16_t trim_offset_us{0};       /// Програмний зсув нейтралі для компенсації дрейфу
};

class ContinuousServo;

/**
 * @brief RAII-обгортка для гарантованої безпечної зупинки сервопривода.
 * Забезпечує автоматичне подання нейтрального ШІМ-імпульсу при виході об'єкта
 * з області видимості або при виникненні виняткових ситуацій.
 */
class ServoGuard {
public:
    explicit ServoGuard(ContinuousServo& servo);
    ~ServoGuard();

    // Забороняємо копіювання для запобігання дублюванню викликів зупинки
    ServoGuard(const ServoGuard&) = delete;
    ServoGuard& operator=(const ServoGuard&) = delete;

    // Переміщення дозволено
    ServoGuard(ServoGuard&& other) noexcept;
    ServoGuard& operator=(ServoGuard&& other) noexcept;

    /**
     * @brief Скасування автоматичної зупинки сервопривода при знищенні об'єкта.
     */
    void release() noexcept;

    /// Перевірка активності захисного механізму
    bool isActive() const noexcept { return active_; }

private:
    ContinuousServo* servo_{nullptr};
    bool active_{true};
};

/**
 * @brief Клас для об'єктно-орієнтованого керування сервоприводом постійного обертання.
 * Трансформує відносну швидкість (-100%..+100%) у керуючий ШІМ-імпульс
 * з урахуванням програмного зсуву нейтральної точки (trim offset).
 */
class ContinuousServo {
public:
    /**
     * @brief Конструктор модуля сервопривода.
     * @param timer Посилання на апаратний ШІМ-таймер.
     * @param config Налаштування часових параметрів ШІМ-імпульсів.
     */
    explicit ContinuousServo(PwmTimer& timer, ServoPwmConfig config = ServoPwmConfig{});

    /**
     * @brief Ініціалізація модуля та переведення вала у нейтральний стан.
     * @return true у разі успішної ініціалізації таймера.
     */
    bool init();

    /**
     * @brief Встановлення швидкості та напрямку обертання.
     * @param speed_percent Значення від -100.0f (max CCW) до +100.0f (max CW).
     *                      0.0f відповідає зупинці.
     */
    void setSpeed(float speed_percent);

    /**
     * @brief Встановлення швидкості з явним зазначенням напрямку.
     * @param direction Напрямок обертання (Clockwise, CounterClockwise, Stop).
     * @param speed_percent Величина швидкості у відсотках (0.0f..100.0f).
     */
    void setSpeed(ServoDirection direction, float speed_percent);

    /**
     * @brief Негайна зупинка обертання вала (подача імпульсу нейтралі).
     */
    void stop();

    /**
     * @brief Налаштування програмного зсуву нейтральної точки (trim offset).
     * Використовується для калібрування та усунення дрейфу потенціометра.
     * @param offset_us Зсув у мікросекундах (наприклад, +20 або -15).
     */
    void setTrimOffset(int16_t offset_us);

    /// Отримання поточного програмного зсуву нейтралі в мкс
    int16_t getTrimOffset() const noexcept { return config_.trim_offset_us; }

    /**
     * @brief Обчислення тривалості ШІМ-імпульсу за відносною швидкістю.
     * @param speed_percent Відносна швидкість (-100.0f..+100.0f).
     * @return Тривалість керуючого імпульсу у мікросекундах.
     */
    uint16_t calculatePulseWidthUs(float speed_percent) const noexcept;

    /// Обчислення дійсного значення нейтралі з урахуванням зсуву
    uint16_t getEffectiveNeutralUs() const noexcept;

    /// Отримання поточної тривалості керуючого імпульсу в мкс
    uint16_t getCurrentPulseUs() const noexcept { return current_pulse_us_; }

    /// Отримання поточної встановленої швидкості у відсотках
    float getCurrentSpeed() const noexcept { return current_speed_; }

    /// Перевірка, чи знаходиться сервопривід у стані зупинки
    bool isStopped() const noexcept;

    /// Отримання конфігураційних параметрів
    const ServoPwmConfig& getConfig() const noexcept { return config_; }

private:
    PwmTimer& timer_;
    ServoPwmConfig config_;
    uint16_t current_pulse_us_{1500};
    float current_speed_{0.0f};
    bool initialized_{false};
};

#endif // CONTINUOUS_SERVO_HPP
