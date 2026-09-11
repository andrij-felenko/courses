#include <cstdint>

class MotorController {
public:
    // Стани кінцевого автомата приводу
    enum class State : uint8_t {
        Coast = 0,   // Вільний вибіг (Hi-Z, обмотка розімкнена)
        Forward,     // Обертання вперед
        Reverse,     // Обертання назад
        Brake,       // Динамічне гальмування (обмотка закорочена)
        Fault        // Аварійне блокування (перевантаження за струмом)
    };

    // Статуси виконання операцій API
    enum class Status : uint8_t {
        Ok = 0,
        InvalidArg,
        FaultActive,
        HardwareFailure
    };

    // Структура апаратної конфігурації та безпеки
    struct Config {
        uint8_t pin_in1;             // Вивід керування першим плечем моста
        uint8_t pin_in2;             // Вивід керування другим плечем моста
        uint8_t pin_pwm;             // Вивід апаратного ШІМ
        uint8_t pin_current_sense;   // Аналоговий вивід датчика струму (АЦП)
        uint32_t pwm_frequency_hz;   // Робоча частота ШІМ, Гц

        uint16_t dead_time_us;       // Пауза мертвого часу, мкс
        float slew_rate_limit;       // Максимальна швидкість наростання швидкості, частка/с
        uint16_t stall_current_ma;   // Поріг струму заклинювання ротора, мА
        uint16_t stall_blanking_ms;  // Інтервал маскування пускового струму, мс
        uint16_t stall_timeout_ms;   // Час перевантаження до переходу в аварію, мс
    };

    explicit MotorController(const Config& config);

    // Ініціалізація виводів та переведення у вихідний стан COAST
    Status init();

    // Задання нормалізованої швидкості зі знаком [-1.0f .. +1.0f]
    Status setSpeed(float speed);

    // Переведення в режим активного динамічного гальмування
    Status brake();

    // Переведення у вільний вибіг (зняття напруги, Hi-Z)
    Status coast();

    // Скидання аварійного стану після усунення причини перевантаження
    Status resetFault();

    // Періодичний крок розрахунку рампи швидкості та моніторингу струму
    Status update(uint32_t delta_time_ms);

    // Методи інспекції стану
    State getState() const { return state_; }
    float getCurrentSpeed() const { return current_speed_; }
    uint16_t getMeasuredCurrent() const { return measured_current_ma_; }

private:
    Config config_;
    State state_{State::Coast};
    float target_speed_{0.0f};
    float current_speed_{0.0f};
    uint16_t measured_current_ma_{0};
    uint32_t stall_timer_ms_{0};
    uint32_t fault_flags_{0};
};
