#ifndef MOC3063_HPP
#define MOC3063_HPP

#include <cstdint>

/**
 * @file Moc3063.hpp
 * @brief Драйвер оптосимістора MOC3063 з вбудованою схемою детектора переходу через нуль (Zero-Cross).
 *
 * Клас Moc3063 забезпечує об'єктно-орієнтоване та безпечне керування силовим ключем 
 * змінної напруги (AC 110V/220V) через GPIO мікроконтролера. 
 *
 * Фізика роботи Zero-Cross:
 * - Вхідний IR-світлодіод оптопари вмикається керуючим сигналом GPIO.
 * - Вбудований детектор нуля відкриває внутрішній фотосимістор ТІЛЬКИ в момент, 
 *   коли напруга AC-мережі проходить через 0V (зменшення електромагнітних завад EMI та кидків струму).
 * - При вимкненні світлодіода силовий симістор закривається при найближчому зниженні струму 
 *   навантаження нижче струму утримання (при наступному переході через 0V).
 */

/// Логічний рівень на виводі GPIO
enum class LogicLevel : uint8_t {
    Low = 0,  ///< Низький рівень (0V / GND)
    High = 1  ///< Високий рівень (VCC / 3.3V / 5V)
};

/// Полярність керування вхідним світлодіодом оптопари
enum class ActiveLevel : uint8_t {
    ActiveLow = 0,  ///< Активний низький рівень (мікроконтролер є споживачем струму / sink)
    ActiveHigh = 1  ///< Активний високий рівень (мікроконтролер є джерелом струму / source)
};

/// Логічний стан комутації мережевого навантаження
enum class LoadState : uint8_t {
    Disabled = 0, ///< Навантаження вимкнено (струм через світлодіод не тече)
    Enabled = 1   ///< Навантаження увімкнено (світлодіод випромінює світло)
};

/// Коди статусів виконання операцій драйвера
enum class Status : uint8_t {
    Ok = 0,                ///< Операція виконана успішно
    InvalidPin,            ///< Некоректний номер виводу GPIO
    NotInitialized,        ///< Драйвер не було ініціалізовано
    AlreadyInitialized,    ///< Драйвер вже ініціалізовано
    HardwareError          ///< Помилка апаратного рівня / HAL
};

/// Типи функцій-зворотного виклику для абстракції периферії GPIO (HAL)
using GpioWriteFn = void (*)(uint8_t pin, LogicLevel level);
using GpioInitFn  = bool (*)(uint8_t pin, LogicLevel inactive_level);

/**
 * @brief Структура конфігурації для створення об'єкта Moc3063.
 */
struct Moc3063Config {
    uint8_t pin{0};                                     ///< Номер виводу GPIO мікроконтролера
    ActiveLevel active_level{ActiveLevel::ActiveHigh}; ///< Активний логічний рівень керування
    LoadState initial_state{LoadState::Disabled};      ///< Початковий стан навантаження при ініціалізації
    GpioWriteFn write_fn{nullptr};                     ///< Вказівник на функцію запису в GPIO
    GpioInitFn init_fn{nullptr};                       ///< Вказівник на функцію налаштування GPIO
};

/**
 * @brief Драйвер оптосимістора MOC3063.
 */
class Moc3063 {
public:
    /**
     * @brief Конструктор драйвера.
     * @param config Структура з параметрами конфігурації GPIO та функціями HAL.
     */
    explicit Moc3063(const Moc3063Config& config) noexcept;

    /**
     * @brief Деструктор. Автоматично вимикає навантаження для безпеки (RAII).
     */
    ~Moc3063() noexcept;

    // Заборона копіювання (один фізичний вивід GPIO не повинен мати дубльованих контролерів)
    Moc3063(const Moc3063&) = delete;
    Moc3063& operator=(const Moc3063&) = delete;

    // Підтримка семантики переміщення
    Moc3063(Moc3063&& other) noexcept;
    Moc3063& operator=(Moc3063&& other) noexcept;

    /**
     * @brief Безпечна ініціалізація виводу GPIO.
     * 
     * Встановлює неактивний логічний рівень ДО переведення виводу в режим виходу (Output),
     * що запобігає короткочасним помилковим сплескам струму на світлодіоді при старті МК.
     * 
     * @return Status::Ok у разі успіху або відповідний код помилки.
     */
    [[nodiscard]] Status init() noexcept;

    /**
     * @brief Ввімкнення навантаження.
     * @return Status Статус виконання операції.
     */
    [[nodiscard]] Status turnOn() noexcept;

    /**
     * @brief Вимкнення навантаження.
     * @return Status Статус виконання операції.
     */
    [[nodiscard]] Status turnOff() noexcept;

    /**
     * @brief Перемикання стану навантаження на протилежний (Toggle).
     * @return Status Статус виконання операції.
     */
    [[nodiscard]] Status toggle() noexcept;

    /**
     * @brief Встановлення потрібного стану навантаження.
     * @param state Бажаний стан (Enabled або Disabled).
     * @return Status Статус виконання операції.
     */
    [[nodiscard]] Status setState(LoadState state) noexcept;

    /**
     * @brief Отримання поточного логічного стану навантаження.
     */
    [[nodiscard]] LoadState getState() const noexcept;

    /**
     * @brief Перевірка, чи увімкнено навантаження.
     */
    [[nodiscard]] bool isEnabled() const noexcept;

    /**
     * @brief Перевірка, чи ініціалізовано драйвер.
     */
    [[nodiscard]] bool isInitialized() const noexcept;

    /**
     * @brief Отримання номера виводу GPIO.
     */
    [[nodiscard]] uint8_t getPin() const noexcept;

private:
    Moc3063Config config_;
    LoadState current_state_{LoadState::Disabled};
    bool is_initialized_{false};

    /**
     * @brief Перетворення логічного стану навантаження в логічний рівень GPIO.
     */
    [[nodiscard]] LogicLevel stateToLogicLevel(LoadState state) const noexcept;
};

#endif // MOC3063_HPP
