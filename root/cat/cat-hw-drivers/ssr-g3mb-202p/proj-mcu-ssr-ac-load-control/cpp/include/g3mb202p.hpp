#ifndef G3MB202P_HPP
#define G3MB202P_HPP

#include <chrono>
#include <cstdint>

namespace drivers {

/**
 * @brief Полярність керуючого сигналу GPIO.
 */
enum class LogicLevel : uint8_t {
    ActiveHigh, // Логічна 1 вмикає реле
    ActiveLow   // Логічний 0 вмикає реле
};

/**
 * @brief Стан твердотільного реле.
 */
enum class RelayState : uint8_t {
    Off = 0,
    On = 1
};

/**
 * @brief Результат виконання операції перемикання.
 */
enum class SwitchResult : uint8_t {
    Success,           // Стан успішно змінено
    AlreadyInState,    // Реле вже перебуває у запрашованому стані
    Throttled          // Зміну стану відхилено через захисний часовий інтервал
};

/**
 * @brief Конфігурація GPIO для керування реле G3MB-202P.
 */
struct GpioConfig {
    uint8_t pin_number{0};                           // Номер цифрового піна GPIO
    LogicLevel active_level{LogicLevel::ActiveHigh}; // Полярність ввімкнення
};

/**
 * @brief Налаштування часових інтервалів безпеки.
 */
struct SafetyConfig {
    std::chrono::milliseconds min_switch_interval{100}; // Мінімальна затримка між перемиканнями (мс)
};

/**
 * @brief Клас-драйвер для твердотільного реле G3MB-202P.
 * 
 * Забезпечує інкапсуляцію стану комутатора, безпечне керування GPIO
 * та програмне обмеження частоти комутації силового навантаження 240 В.
 */
class G3MB202P {
public:
    /**
     * @brief Конструктор драйвера реле.
     * @param gpio_cfg Конфігурація цифрового виводу.
     * @param safety_cfg Налаштування часового захисту від надчастої комутації.
     */
    explicit G3MB202P(GpioConfig gpio_cfg, SafetyConfig safety_cfg = {});

    /**
     * @brief Деструктор. Автоматично переводить реле у безпечний стан (Off).
     */
    ~G3MB202P();

    // Забороняємо копіювання для запобігання дублюванню керування одним піном
    G3MB202P(const G3MB202P&) = delete;
    G3MB202P& operator=(const G3MB202P&) = delete;

    // Дозволяємо переміщення
    G3MB202P(G3MB202P&&) noexcept = default;
    G3MB202P& operator=(G3MB202P&&) noexcept = default;

    /**
     * @brief Ініціалізація апаратного GPIO піна.
     * @return true у разі успішного налаштування піна.
     */
    bool init();

    /**
     * @brief Увімкнути навантаження 240 В.
     * @param force Якщо true, ігнорує обмеження частоти (використовувати з обережністю).
     * @return Результат спроби перемикання.
     */
    SwitchResult turn_on(bool force = false);

    /**
     * @brief Вимкнути навантаження 240 В.
     * @param force Якщо true, ігнорує обмеження частоти.
     * @return Результат спроби перемикання.
     */
    SwitchResult turn_off(bool force = false);

    /**
     * @brief Перемикнути стан реле на протилежний.
     * @return Результат спроби перемикання.
     */
    SwitchResult toggle();

    /**
     * @brief Отримати поточний стан реле.
     */
    RelayState state() const noexcept { return current_state_; }

    /**
     * @brief Перевірити, чи реле увімкнене.
     */
    bool is_on() const noexcept { return current_state_ == RelayState::On; }

    /**
     * @brief Перевірити, чи пройшов мінімальний захисний інтервал для наступного перемикання.
     */
    bool can_switch() const noexcept;

    /**
     * @brief Отримати час, що залишився до дозволу наступного перемикання.
     */
    std::chrono::milliseconds time_until_next_switch() const noexcept;

private:
    void write_pin_hardware(bool level);
    SwitchResult apply_state(RelayState new_state, bool force);

    GpioConfig gpio_cfg_;
    SafetyConfig safety_cfg_;
    RelayState current_state_{RelayState::Off};
    bool is_initialized_{false};

    using clock = std::chrono::steady_clock;
    clock::time_point last_switch_time_{clock::time_point::min()};
};

} // namespace drivers

#endif // G3MB202P_HPP
