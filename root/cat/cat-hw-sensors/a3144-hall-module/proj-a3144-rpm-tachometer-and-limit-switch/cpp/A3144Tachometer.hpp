#ifndef A3144_TACHOMETER_HPP
#define A3144_TACHOMETER_HPP

#include <cstdint>
#include <functional>
#include <atomic>

/**
 * @file A3144Tachometer.hpp
 * @brief Оголошення класу A3144Tachometer для вимірювання обертів за хвилину (RPM)
 *        за допомогою цифрового давача Холла A3144.
 */

/// Конфігураційна структура параметрів тахометра
struct TachometerConfig {
    uint8_t gpio_pin{2};                    ///< Номер виводу GPIO з підтримкою зовнішніх переривань (EXTI)
    uint8_t magnets_per_revolution{1};     ///< Кількість магнітів, закріплених на валу (мінімум 1)
    uint32_t debounce_interval_us{2000};   ///< Інтервал придушення брязкоту контактів у мікросекундах (2 мс)
    uint32_t timeout_us{2000000};          ///< Таймаут відсутності імпульсів (2 секунди), після якого RPM = 0
};

/// Тип функціонального обробника події оновлення швидкості
using TachometerCallback = std::function<void(float rpm, uint32_t totalPulses)>;

/**
 * @class A3144Tachometer
 * @brief Драйвер цифрового тахометра на базі давача Холла A3144.
 *
 * Клас інкапсулює низькорівневу обробку апаратних переривань через статичний місток (ISR bridge),
 * виконує програмну фільтрацію цифрового шуму (дебаунсинг), вимірює часові інтервали між
 * імпульсами магніту та обчислює швидкість обертання у реальному часі (RPM).
 */
class A3144Tachometer {
public:
    /**
     * @brief Конструктор об'єкта тахометра
     * @param config Налаштування периферії та вимірювального процесу
     */
    explicit A3144Tachometer(const TachometerConfig& config = TachometerConfig{});

    /**
     * @brief Деструктор класу. Зупиняє обробку переривань.
     */
    ~A3144Tachometer();

    // Заборона копіювання для збереження єдиного зв'язку з апаратним перериванням
    A3144Tachometer(const A3144Tachometer&) = delete;
    A3144Tachometer& operator=(const A3144Tachometer&) = delete;

    /**
     * @brief Ініціалізація периферійного виводу GPIO та активація переривань EXTI
     * @return true, якщо об'єкт успішно зв'язано з апаратним обробником
     */
    bool begin();

    /**
     * @brief Відкріплення переривання та деактивація драйвера
     */
    void stop();

    /**
     * @brief Періодичний неблокувальний крок оновлення (викликається в main/loop)
     *        Обробляє таймаути зупинки та викликає зареєстровані callback-функції.
     */
    void update();

    /**
     * @brief Реєстрація користувацької callback-функції для подій оновлення показань
     * @param callback Лямбда-вираз або функціональний об'єкт
     */
    void registerCallback(TachometerCallback callback);

    /**
     * @brief Отримання поточної швидкості обертання у RPM
     * @return Значення обертів за хвилину
     */
    [[nodiscard]] float getRPM() const noexcept;

    /**
     * @brief Отримання загальної кількості підрахованих імпульсів
     * @return Загальна кількість імпульсів
     */
    [[nodiscard]] uint32_t getPulseCount() const noexcept;

    /**
     * @brief Скидання лічильника імпульсів та розрахованого значення RPM
     */
    void reset() noexcept;

    /**
     * @brief Зміна кількості магнітів на валу
     * @param count Кількість магнітів (count >= 1)
     */
    void setMagnetsPerRevolution(uint8_t count) noexcept;

    /**
     * @brief Отримання поточних налаштувань тахометра
     */
    [[nodiscard]] const TachometerConfig& getConfig() const noexcept { return config_; }

    /**
     * @brief Статична функція-місток обробника переривань (ISR bridge)
     */
    static void handleInterruptBridge();

    /**
     * @brief Симуляція імпульсу від давача Холла для тестування
     * @param timestamp_us Поточна мітка часу в мікросекундах
     */
    void simulatePulse(uint64_t timestamp_us);

private:
    /**
     * @brief Внутрішній обробник переривання конкретного екземпляра
     * @param timestamp_us Поточна мітка часу в мікросекундах
     */
    void handleInterrupt(uint64_t timestamp_us);

    TachometerConfig config_;

    // Атомарні змінні для потокобезпечного обміну між ISR та головним циклом
    std::atomic<uint64_t> last_pulse_time_us_{0};   ///< Час останнього дійсного імпульсу (мкс)
    std::atomic<uint32_t> last_interval_us_{0};     ///< Інтервал між імпульсами (мкс)
    std::atomic<uint32_t> total_pulses_{0};         ///< Загальний лічильник імпульсів
    std::atomic<bool> new_pulse_flag_{false};       ///< Прапор появи нового імпульсу

    float current_rpm_{0.0f};                        ///< Останнє розраховане значення RPM
    bool is_initialized_{false};                    ///< Стан ініціалізації драйвера
    TachometerCallback user_callback_{nullptr};      ///< Зареєстрований callback

    static A3144Tachometer* s_instance;             ///< Статичний вказівник на активний екземпляр
};

#endif // A3144_TACHOMETER_HPP
