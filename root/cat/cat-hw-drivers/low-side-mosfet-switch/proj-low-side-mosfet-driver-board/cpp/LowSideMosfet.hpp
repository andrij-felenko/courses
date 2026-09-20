#ifndef LOW_SIDE_MOSFET_HPP
#define LOW_SIDE_MOSFET_HPP

#include <cstdint>

/**
 * @brief Стан драйвера силового низькостороннього MOSFET-ключа.
 */
enum class DriverState {
    Uninitialized,  ///< Драйвер не ініціалізований, затвор притиснутий до землі
    Disabled,       ///< Драйвер ініціалізований, але вихід ШІМ вимкнений (0V)
    Active,         ///< Драйвер активний, генерується ШІМ-сигнал
    Fault           ///< Аварійний стан або помилка параметрів
};

/**
 * @brief Конфігурація апаратних параметрів ключа та ШІМ-таймера.
 */
struct MosfetConfig {
    uint8_t gpioPin;            ///< Номер пина мікроконтролера, підключеного до затвора (Gate)
    uint32_t pwmFrequencyHz;    ///< Початкова частота ШІМ у Герцах (наприклад, 1000...20000 Гц)
    float initialDutyCycle;     ///< Початковий коефіцієнт заповнення у відсотках (0.0%..100.0%)
    bool invertedLogic;         ///< Інверсія сигналу (false: High = ON, true: Low = ON)
    uint32_t timerClockHz;      ///< Тактова частота таймера МК у Гц (наприклад, 16 000 000 Гц)
};

/**
 * @brief Клас для безпечного об'єктно-орієнтованого керування силовим N-канальним
 *        MOSFET-ключем у низькосторонній схемі (Low-Side Switch) за допомогою ШІМ.
 */
class LowSideMosfet {
public:
    /**
     * @brief Конструктор за замовчуванням.
     */
    LowSideMosfet();

    /**
     * @brief Деструктор. Автоматично знеструмлює навантаження для безпеки.
     */
    ~LowSideMosfet();

    // Забороняємо копіювання об'єкта для уникнення колізій керування апаратним пином
    LowSideMosfet(const LowSideMosfet&) = delete;
    LowSideMosfet& operator=(const LowSideMosfet&) = delete;

    /**
     * @brief Безпечна ініціалізація апаратного виводу та ШІМ-таймера.
     * @param config Конфігурація драйвера.
     * @return true у разі успіху, false при некоректних параметрах.
     */
    bool begin(const MosfetConfig& config);

    /**
     * @brief Встановлення коефіцієнта заповнення ШІМ (Duty Cycle) у відсотках.
     * @param percent Коефіцієнт заповнення від 0.0% (повністю вимкнено) до 100.0% (повністю увімкнено).
     */
    void setDutyCycle(float percent);

    /**
     * @brief Отримання поточного коефіцієнта заповнення ШІМ у відсотках.
     * @return Значення від 0.0 до 100.0%.
     */
    float getDutyCycle() const;

    /**
     * @brief Динамічна зміна частоти ШІМ-сигналу.
     * @param frequencyHz Нова частота в Гц.
     * @return true, якщо частоту успішно перераховано.
     */
    bool setFrequency(uint32_t frequencyHz);

    /**
     * @brief Отримання поточної частоти ШІМ.
     * @return Частота в Гц.
     */
    uint32_t getFrequency() const;

    /**
     * @brief Плавне регулювання потужності (плавний пуск / згасання).
     * @param targetPercent Цільовий коефіцієнт заповнення у відсотках (0.0%..100.0%).
     * @param durationMs Тривалість плавного переходу в мілісекундах.
     * @param stepMs Інтервал між кроками регулювання в мілісекундах (за замовчуванням 10 мс).
     */
    void rampPower(float targetPercent, uint32_t durationMs, uint32_t stepMs = 10);

    /**
     * @brief Негайне аварійне вимкнення силового ключа (примусовий 0V на затворі).
     */
    void emergencyStop();

    /**
     * @brief Увімкнення генерації ШІМ-сигналу.
     */
    void enable();

    /**
     * @brief Вимкнення ШІМ-сигналу (затвор переводиться в стан LOW).
     */
    void disable();

    /**
     * @brief Перевірка, чи активний ключ.
     * @return true, якщо ШІМ увімкнено.
     */
    bool isEnabled() const;

    /**
     * @brief Отримання поточного стану драйвера.
     * @return Перелічувальне значення DriverState.
     */
    DriverState getState() const;

private:
    MosfetConfig m_config;
    DriverState m_state;
    float m_currentDutyCycle;
    uint32_t m_currentArr;      ///< Значення регістру автоперезавантаження таймера (Auto-Reload Register)
    uint32_t m_currentCcr;      ///< Значення регістру порівняння (Capture/Compare Register)
    bool m_enabled;

    /**
     * @brief Перерахунок регістрів таймера (ARR та CCR) на основі частоти та duty cycle.
     */
    bool recalculateTimerRegisters(uint32_t frequencyHz, float dutyPercent);

    /**
     * @brief Передача обчислених значень у регістри апаратної периферії МК.
     */
    void updateHardwareRegisters();

    /**
     * @brief Початкова безпечна настройка GPIO (OUTPUT з притисненням Pull-Down).
     */
    void setupSafePinState();
};

#endif // LOW_SIDE_MOSFET_HPP
