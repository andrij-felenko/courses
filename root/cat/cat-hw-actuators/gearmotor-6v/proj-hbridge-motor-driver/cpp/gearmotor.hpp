#pragma once

#include <cstdint>
#include <cstddef>

namespace actuators {

/**
 * @brief Фізичний стан комутації ключів H-моста.
 */
enum class State : uint8_t {
    STOP_COAST = 0, ///< Вільний вибіг: ключі розімкнені (High-Z), вал обертається за інерцією
    FORWARD    = 1, ///< Рух уперед: активна діагональ Q1 (верхній лівий) + Q4 (нижній правий)
    REVERSE    = 2, ///< Реверс: активна діагональ Q3 (верхній правий) + Q2 (нижній лівий)
    BRAKE      = 3  ///< Динамічне гальмування: обидва нижні ключі Q2+Q4 замкнені на шину GND
};

/**
 * @brief Напрямок обертання вихідного вала приводу.
 */
enum class Direction : int8_t {
    REVERSE = -1, ///< Обертання проти годинникової стрілки (від'ємна швидкість)
    STOP    =  0, ///< Повна зупинка вала
    FORWARD =  1  ///< Обертання за годинниковою стрілкою (додатна швидкість)
};

/**
 * @brief Призначення пінів мікроконтролера для керування H-мостом.
 */
struct Pins {
    uint8_t in1{0}; ///< Пін напрямку/напівмоста 1 (IN1)
    uint8_t in2{0}; ///< Пін напрямку/напівмоста 2 (IN2)
    uint8_t pwm{0}; ///< Пін таймера ШІМ (дозвіл роботи / EN / PWM)
};

/// Зворотний виклик для дискретного запису GPIO (апаратний рівень HAL)
using GpioWriteFn = void (*)(uint8_t pin, bool level);

/// Зворотний виклик для виводу шпаруватості ШІМ (апаратний таймер)
using PwmWriteFn  = void (*)(uint8_t pin, uint16_t duty);

/**
 * @brief Параметри конфігурації приводу та апаратні виклики.
 */
struct Config {
    Pins pins{};                   ///< Призначення ліній мікроконтролера
    uint16_t maxDuty{1000};        ///< Максимальна шпаруватість ШІМ (дискрети шкали, 1000 = 100%)
    uint16_t accelRate{800};       ///< Темп розгону: одиниць шпаруватості за 1 секунду
    uint16_t decelRate{1600};      ///< Темп уповільнення: одиниць шпаруватості за 1 секунду
    uint32_t deadTimeMs{30};       ///< Захисний інтервал dead-time (мс) при зміні полярності
    GpioWriteFn writeGpio{nullptr};///< Функція запису дискретного піна (HAL)
    PwmWriteFn  writePwm{nullptr}; ///< Функція запису таймера ШІМ (HAL)
};

/**
 * @brief Драйвер 6-вольтового мотор-редуктора з захистом від струмових та ударних навантажень.
 * 
 * Реалізує:
 * 1. Безпечну комутацію H-моста з алгоритмом "break-before-make" для захисту від наскрізних струмів.
 * 2. Лінійне наростання (акселерація) та спадання (деселерація) ШІМ для збереження шестерень редуктора.
 * 3. Автоматичний перехід через нульову швидкість і захисну паузу (dead-time) під час реверсу.
 * 4. Два режими зупинки: вільний вибіг (coast) та електродинамічне активне гальмування (brake).
 * 5. Повністю статичне виділення пам'яті (no heap, zero-cost abstraction).
 */
class Gearmotor {
public:
    /**
     * @brief Конструктор приводу з конфігурацією.
     * @param config Налаштування пінів, темпів розгону та вказівників на HAL.
     */
    explicit Gearmotor(const Config& config) noexcept;

    /**
     * @brief Ініціалізація апаратних ліній та скидання ключів у захисний стан.
     * @return true у разі успішної ініціалізації валідних вказівників HAL.
     */
    bool init() noexcept;

    /**
     * @brief Задати цільову швидкість зі знаком (-maxDuty .. +maxDuty).
     * @param targetSpeed Додатні значення — рух уперед, від'ємні — назад, 0 — плавна зупинка.
     */
    void setSpeed(int16_t targetSpeed) noexcept;

    /**
     * @brief Задати напрямок і шпаруватість окремими аргументами.
     * @param dir Напрямок (FORWARD, REVERSE, STOP).
     * @param duty Шпаруватість ШІМ (0 .. maxDuty).
     */
    void setTarget(Direction dir, uint16_t duty) noexcept;

    /**
     * @brief Активне електродинамічне гальмування (коротке замикання обмоток на GND).
     * Створює протидіючий електромагнітний момент за рахунок струму проти-ЕРС.
     */
    void brake() noexcept;

    /**
     * @brief Вільний вибіг (розмикання всіх ключів моста, високий опір).
     * Ротор поступово зупиняється виключно механічним тертям редуктора.
     */
    void coast() noexcept;

    /**
     * @brief Періодичний неблоківний розрахунок рампи ШІМ та станів моста.
     * @param deltaMs Час у мілісекундах від попереднього виклику.
     */
    void update(uint32_t deltaMs) noexcept;

    /// Поточна реальна шпаруватість ШІМ на мості (0 .. maxDuty)
    [[nodiscard]] uint16_t getCurrentDuty() const noexcept { return m_currentDuty; }

    /// Задана цільова шпаруватість ШІМ
    [[nodiscard]] uint16_t getTargetDuty() const noexcept { return m_targetDuty; }

    /// Поточний стан ключів H-моста
    [[nodiscard]] State getState() const noexcept { return m_state; }

    /// Активний напрямок обертання мотора
    [[nodiscard]] Direction getDirection() const noexcept { return m_activeDir; }

    /// Чи перебуває міст у стані захисної паузи реверсу (dead-time)
    [[nodiscard]] bool isInDeadTime() const noexcept { return m_deadTimeRemainingMs > 0; }

    /// Чи триває перехідний процес зміни швидкості або реверсу
    [[nodiscard]] bool isRamping() const noexcept;

private:
    /**
     * @brief Безпечне оновлення станів транзисторів H-моста за таблицею комутації.
     */
    void applyHBridge(State state, uint16_t duty) noexcept;

    Config m_config;

    State     m_state{State::STOP_COAST};        ///< Поточний комутаційний стан моста
    Direction m_activeDir{Direction::STOP};      ///< Поточний активний напрямок обертання
    Direction m_targetDir{Direction::STOP};      ///< Заданий цільовий напрямок обертання

    uint16_t  m_currentDuty{0};                  ///< Поточна шпаруватість ШІМ
    uint16_t  m_targetDuty{0};                   ///< Цільова шпаруватість ШІМ

    uint32_t  m_deadTimeRemainingMs{0};          ///< Лічильник залишку захисної паузи (мс)
    uint32_t  m_rampAccumulator{0};              ///< Накопичувач для точного інтегрування темпу рампи
    bool      m_brakeActive{false};              ///< Прапорець примусового активного гальмування
};

} // namespace actuators
