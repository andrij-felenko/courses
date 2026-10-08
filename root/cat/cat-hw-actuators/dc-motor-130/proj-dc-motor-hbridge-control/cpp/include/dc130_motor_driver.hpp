#ifndef DC130_MOTOR_DRIVER_HPP
#define DC130_MOTOR_DRIVER_HPP

#include "pwm_timer.hpp"
#include <cstdint>

namespace embedded {

/**
 * @brief Напрямок обертання вала мотора.
 */
enum class Direction {
    Forward, ///< Обертання Вперед
    Reverse  ///< Обертання Назад
};

/**
 * @brief Режим зупинки колекторного мотора H-мостом.
 */
enum class StopMode {
    Coast, ///< Вільний інерційний вибіг (Hi-Z стан ключів)
    Brake  ///< Активне електродинамічне гальмування (коротке замикання обмоток)
};

/**
 * @brief Структура параметрів конфігурації мотора типорозміру 130.
 */
struct MotorConfig {
    uint8_t pinIn1{1};              ///< Вивід керування IN1
    uint8_t pinIn2{2};              ///< Вивід керування IN2
    uint8_t pinEnable{3};           ///< Вивід ШІМ (EN)
    uint32_t pwmFrequencyHz{20000}; ///< Частота ШІМ (Гц)
    uint32_t deadTimeMs{50};        ///< Інтервал Dead Time при реверсі (мс)
    uint8_t minDutyCycle{10};       ///< Поріг подолання тертя спокою 130-го мотора (%)
};

/**
 * @brief Клас об'єктно-орієнтованого драйвера колекторного двигуна типорозміру 130.
 * 
 * Надає високорівневий інтерфейс керування швідкістю setSpeed(), напрямком setDirection()
 * із програмним захистом Dead Time, а також реалізує режими активного гальмування brake()
 * та інерційного вибігу coast().
 */
class DC130MotorDriver {
public:
    /**
     * @brief Конструктор драйвера.
     * @param config Налаштування GPIO та параметрів ШІМ
     */
    explicit DC130MotorDriver(const MotorConfig& config);

    ~DC130MotorDriver();

    DC130MotorDriver(const DC130MotorDriver&) = delete;
    DC130MotorDriver& operator=(const DC130MotorDriver&) = delete;

    DC130MotorDriver(DC130MotorDriver&&) noexcept = default;
    DC130MotorDriver& operator=(DC130MotorDriver&&) noexcept = default;

    /**
     * @brief Ініціалізація підсистеми керування мотором.
     */
    bool init();

    /**
     * @brief Встановлення швидкості обертання (0–100%).
     * @param percent Відсоток від максимальної швидкості
     */
    void setSpeed(uint8_t percent);

    /**
     * @brief Встановлення напрямку обертання з автозахистом Dead Time при реверсі.
     * @param dir Бажаний напрямок обертання (Forward / Reverse)
     */
    void setDirection(Direction dir);

    /**
     * @brief Активне електродинамічне гальмування вала мотора.
     * 
     * Замикає обмотки двигуна накопиченою проти-ЕРС, створюючи потужний гальмівний момент.
     */
    void brake();

    /**
     * @brief Вільний інерційний вибіг мотора.
     * 
     * Розмикає транзистори H-моста у високоімпедансний стан Z, дозволяючи мотору вільно зупинитися.
     */
    void coast();

    [[nodiscard]] uint8_t getSpeed() const noexcept { return currentSpeed_; }
    [[nodiscard]] Direction getDirection() const noexcept { return currentDirection_; }
    [[nodiscard]] bool isRunning() const noexcept { return isRunning_; }
    [[nodiscard]] StopMode getLastStopMode() const noexcept { return lastStopMode_; }

private:
    MotorConfig config_;
    PwmTimer timer_;
    Direction currentDirection_{Direction::Forward};
    uint8_t currentSpeed_{0};
    bool isRunning_{false};
    StopMode lastStopMode_{StopMode::Coast};

    void executeDeadTime();
    void applyDirectionPins();
};

/**
 * @brief RAII-обгортка для гарантованої безпечної зупинки мотора при виході з області видимості.
 */
class MotorGuard {
public:
    explicit MotorGuard(DC130MotorDriver& driver, StopMode safeMode = StopMode::Coast) noexcept;
    ~MotorGuard();

    MotorGuard(const MotorGuard&) = delete;
    MotorGuard& operator=(const MotorGuard&) = delete;

    MotorGuard(MotorGuard&& other) noexcept;
    MotorGuard& operator=(MotorGuard&& other) noexcept;

    /**
     * @brief Відвід захисника від виконання зупинки.
     */
    void dismiss() noexcept;

private:
    DC130MotorDriver* driver_{nullptr};
    StopMode safeMode_{StopMode::Coast};
    bool active_{true};
};

} // namespace embedded

#endif // DC130_MOTOR_DRIVER_HPP
