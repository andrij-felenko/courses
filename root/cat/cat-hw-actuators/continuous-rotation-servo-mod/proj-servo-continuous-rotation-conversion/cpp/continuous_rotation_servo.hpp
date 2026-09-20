#ifndef CONTINUOUS_ROTATION_SERVO_HPP_
#define CONTINUOUS_ROTATION_SERVO_HPP_

#include <cstdint>
#include <algorithm>
#include <cmath>

namespace motion {

/**
 * @brief Апаратний інтерфейс ШІМ-виходу таймера мікроконтролера.
 * Забезпечує переносність серводрайвера між різними апаратними платформами
 * (ESP32 MCPWM/LEDC, STM32 TIM, AVR Timer1 тощо).
 */
class IPwmOutput {
public:
    virtual ~IPwmOutput() = default;

    /**
     * @brief Встановлює тривалість активного імпульсу ШІМ у мікросекундах.
     * @param pulse_us Тривалість високого рівня сигналу в мікросекундах (зазвичай 1000..2000 мкс).
     */
    virtual void write_pulse_us(uint16_t pulse_us) noexcept = 0;

    /**
     * @brief Зупиняє генерацію ШІМ-імпульсів (переводить вивід у стан спокою).
     * Знеструмлює силовий каскад сервопривода для запобігання нагріву двигуна.
     */
    virtual void disable() noexcept = 0;

    /**
     * @brief Відновлює генерацію періодичних імпульсів ШІМ на апаратному виводі.
     */
    virtual void enable() noexcept = 0;

    /**
     * @brief Перевіряє, чи активна наразі генерація керувального сигналу.
     * @return true якщо ШІМ-таймер активний, false якщо вимкнений.
     */
    [[nodiscard]] virtual bool is_active() const noexcept = 0;
};

/**
 * @brief Параметри індивідуального калібрування сервопривода постійного обертання.
 * Дозволяє програмно компенсувати асиметрію і температурний дрейф дільника напруги.
 */
struct ServoCalibration {
    uint16_t neutral_us{1500};    ///< Фактична тривалість імпульсу спокою (центральна точка без обертання)
    uint16_t deadband_us{20};     ///< Напівширина мертвої зони (мкс), у межах якої гарантовано відсутній рух
    uint16_t min_pulse_us{1000};  ///< Мінімальна тривалість імпульсу (повний хід у зворотному напрямку)
    uint16_t max_pulse_us{2000};  ///< Максимальна тривалість імпульсу (повний хід у прямому напрямку)
    bool inverted{false};         ///< Прапорець реверсу напрямку обертання (програмна інверсія полярності)

    /**
     * @brief Валідує несуперечливість калібрувальних меж.
     * @return true якщо параметри коректні та безпечні для роботи, false при помилці конфігурації.
     */
    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return (min_pulse_us < neutral_us) &&
               (neutral_us < max_pulse_us) &&
               (deadband_us > 0) &&
               (min_pulse_us <= (neutral_us - deadband_us)) &&
               ((neutral_us + deadband_us) <= max_pulse_us);
    }
};

/**
 * @brief Стан скінченного автомата керування динамікою сервопривода.
 */
enum class DriveState : uint8_t {
    Detached = 0,   ///< Привод знеструмлено (генерацію імпульсів зупинено)
    Stopped,        ///< Вал у стані спокою на нейтральній тривалості
    Running,        ///< Плавне обертання з поточною ненульовою швидкістю
    ReversingDwell  ///< Безпечна мікропауза на нульовій швидкості під час зміни напрямку
};

/**
 * @brief Драйвер сервопривода постійного обертання для вбудованих систем.
 * 
 * Особливості архітектури:
 * - Робота без використання динамічної пам'яті (no heap allocation).
 * - Кусочно-лінійний перерахунок швидкості [-100%..+100%] з компенсацією зміщення нейтралі та мертвої смуги.
 * - Неблокувальний рампінг прискорення dω/dt для згладжування ударів по редуктору та усунення просідань живлення.
 * - Безпечний реверс обертання виключно через стан нульової швидкості з часом стабілізації (dwell time).
 * - Підтримка переведення в режим знеструмлення (detach) під час простою для захисту обмоток від перегріву.
 */
class ContinuousRotationServo {
public:
    /**
     * @brief Конструктор сервопривода постійного обертання.
     * @param pwm Посилання на апаратний інтерфейс виводу ШІМ.
     * @param cal Структура калібрувальних параметрів (за замовчуванням номінальні 1500 мкс).
     * @param max_accel_pct_per_s Максимальне кутове прискорення вала (% швидкості за секунду).
     * @param reverse_dwell_ms Час обов'язкової витримки на нулі перед перемиканням напрямку (мс).
     */
    explicit ContinuousRotationServo(
        IPwmOutput& pwm,
        const ServoCalibration& cal = ServoCalibration{},
        float max_accel_pct_per_s = 200.0f,
        uint32_t reverse_dwell_ms = 40
    ) noexcept;

    /**
     * @brief Встановлює цільову швидкість обертання вала у діапазоні [-100.0% .. +100.0%].
     * @param speed_percent Цільова швидкість: від -100% (реверс) через 0% (стоп) до +100% (вперед).
     */
    void set_speed(float speed_percent) noexcept;

    /**
     * @brief Періодичний крок розрахунку лінійного рампінгу швидкості та оновлення таймера ШІМ.
     * Викликається без блокування в головному суперциклі колісної платформи.
     * @param current_time_ms Поточний монотонний системний час у мілісекундах.
     */
    void update(uint32_t current_time_ms) noexcept;

    /**
     * @brief Знеструмлює привід (вимикає генерацію імпульсів таймера).
     * Захищає двигун від перегріву та заощаджує заряд акумулятора під час стоянки.
     */
    void detach() noexcept;

    /**
     * @brief Відновлює генерацію імпульсів керування та активує сервопривод.
     */
    void attach() noexcept;

    /**
     * @brief Екстрена миттєва зупинка вала у точку спокою без проходження рампінгу.
     */
    void stop_immediately() noexcept;

    /**
     * @brief Налаштовує граничне прискорення (темп наростання швидкості dω/dt).
     * @param max_accel_pct_per_s Допустиме прискорення у %/с (> 0).
     */
    void set_acceleration(float max_accel_pct_per_s) noexcept;

    /**
     * @brief Оновлює індивідуальні калібрувальні параметри нейтралі та мертвої смуги.
     * @param cal Нова структура калібрування.
     * @return true якщо калібрування валідне та збережене, false якщо параметри некоректні.
     */
    bool set_calibration(const ServoCalibration& cal) noexcept;

    /**
     * @brief Задає тривалість захисної мікропаузи спокою під час реверсу.
     * @param dwell_ms Час стабілізації редуктора у мілісекундах.
     */
    void set_reverse_dwell_ms(uint32_t dwell_ms) noexcept;

    /**
     * @brief Перераховує нормалізовану швидкість [-100%..+100%] у ширину імпульсу ШІМ (мкс).
     * Враховує мертву зону (deadband), інверсію та асиметрію плечей ходу навколо нейтралі.
     * @param speed_pct Нормалізована швидкість у відсотках.
     * @return Розрахована тривалість активного імпульсу ШІМ у мікросекундах.
     */
    [[nodiscard]] uint16_t speed_to_pulse(float speed_pct) const noexcept;

    [[nodiscard]] float target_speed() const noexcept { return target_speed_pct_; }
    [[nodiscard]] float current_speed() const noexcept { return current_speed_pct_; }
    [[nodiscard]] uint16_t current_pulse_us() const noexcept { return current_pulse_us_; }
    [[nodiscard]] bool is_attached() const noexcept { return is_attached_; }
    [[nodiscard]] DriveState state() const noexcept { return state_; }
    [[nodiscard]] const ServoCalibration& calibration() const noexcept { return cal_; }
    [[nodiscard]] float max_acceleration() const noexcept { return max_accel_pct_per_s_; }
    [[nodiscard]] uint32_t reverse_dwell_ms() const noexcept { return reverse_dwell_ms_; }

private:
    void apply_pulse(uint16_t pulse_us) noexcept;

    IPwmOutput& pwm_;
    ServoCalibration cal_;
    float max_accel_pct_per_s_{200.0f};
    uint32_t reverse_dwell_ms_{40};

    float target_speed_pct_{0.0f};
    float current_speed_pct_{0.0f};
    uint16_t current_pulse_us_{1500};

    DriveState state_{DriveState::Detached};
    bool is_attached_{false};
    uint32_t last_update_ms_{0};
    uint32_t dwell_start_ms_{0};
};

} // namespace motion

#endif // CONTINUOUS_ROTATION_SERVO_HPP_
