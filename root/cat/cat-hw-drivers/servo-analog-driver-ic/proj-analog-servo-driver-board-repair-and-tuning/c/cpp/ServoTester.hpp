#pragma once

#include <cstdint>
#include <algorithm>

namespace ServoControl {

/**
 * @brief Структура для прямої симуляції/доступу до регістрів апаратного таймера MCU.
 */
struct HardwareTimerRegisters {
    volatile std::uint32_t CR1{0};   //!< Control register 1
    volatile std::uint32_t PSC{0};   //!< Prescaler register
    volatile std::uint32_t ARR{0};   //!< Auto-reload register (Period)
    volatile std::uint32_t CCR1{0};  //!< Capture/Compare register 1 (Pulse width)
    volatile std::uint32_t CCER{0};  //!< Capture/Compare enable register
};

/**
 * @brief Клас для керування аналоговими серводрайверами AA5188 / KC0032 через ШІМ 50 Гц.
 *
 * Інкапсулює конфігурацію апаратного таймера мікроконтролера та надає
 * безпечний інтерфейс для регулювання тривалості імпульсу 1000..2000 мкс або кута 0..180°.
 */
class ServoTester {
public:
    // Константи параметрів ШІМ серводрайверів
    static constexpr std::uint32_t PWM_FREQ_HZ{50};
    static constexpr std::uint32_t PERIOD_US{20000};
    static constexpr std::uint16_t MIN_PULSE_US{1000};
    static constexpr std::uint16_t NEUTRAL_PULSE_US{1500};
    static constexpr std::uint16_t MAX_PULSE_US{2000};

    static constexpr float MIN_ANGLE_DEG{0.0f};
    static constexpr float MAX_ANGLE_DEG{180.0f};

    /**
     * @brief Конструктор із можливістю вказати тактову частоту шини таймера.
     * @param systemClockHz Частота тактування таймера у Гц (за замовчуванням 72 МГц).
     */
    explicit ServoTester(std::uint32_t systemClockHz = 72000000U) noexcept;

    ~ServoTester();

    // Заборона копіювання через зв'язок з апаратним ресурсом
    ServoTester(const ServoTester&) = delete;
    ServoTester& operator=(const ServoTester&) = delete;

    // Дозвіл переміщення
    ServoTester(ServoTester&& other) noexcept;
    ServoTester& operator=(ServoTester&& other) noexcept;

    /**
     * @brief Ініціалізація апаратного таймера.
     * @return true, якщо частота тактування валідна і таймер налаштовано.
     */
    bool init() noexcept;

    /**
     * @brief Запуск генерації ШІМ.
     */
    void start() noexcept;

    /**
     * @brief Зупинка генерації ШІМ.
     */
    void stop() noexcept;

    /**
     * @brief Встановити ширину імпульсу в мікросекундах.
     * @param microseconds Тривалість імпульсу (обрізається до 1000..2000 мкс).
     */
    void setPulseWidthUs(std::uint16_t microseconds) noexcept;

    /**
     * @brief Встановити кут сервоприводу в градусах (0.0..180.0°).
     * @param degrees Кут у градусах.
     */
    void setAngleDeg(float degrees) noexcept;

    /**
     * @brief Отримати поточну тривалість імпульсу в мкс.
     */
    [[nodiscard]] std::uint16_t pulseWidthUs() const noexcept { return currentPulseUs_; }

    /**
     * @brief Отримати поточний кут у градусах.
     */
    [[nodiscard]] float angleDeg() const noexcept;

    /**
     * @brief Перевірити, чи активний ШІМ.
     */
    [[nodiscard]] bool isRunning() const noexcept { return active_; }

    /**
     * @brief Встановити нейтральну позицію (1500 мкс) для калібрування AA5188 / KC0032.
     */
    void calibrateNeutral() noexcept;

    /**
     * @brief Прямий доступ до симульованого блоку регістрів (для налагодження).
     */
    [[nodiscard]] const HardwareTimerRegisters& timerRegisters() const noexcept { return timerRegs_; }

private:
    HardwareTimerRegisters timerRegs_{};
    std::uint32_t systemClockHz_;
    std::uint16_t currentPulseUs_{NEUTRAL_PULSE_US};
    bool active_{false};

    static constexpr std::uint32_t TIM_CR1_CEN{1U << 0};
    static constexpr std::uint32_t TIM_CCER_CC1E{1U << 0};
};

} // namespace ServoControl
