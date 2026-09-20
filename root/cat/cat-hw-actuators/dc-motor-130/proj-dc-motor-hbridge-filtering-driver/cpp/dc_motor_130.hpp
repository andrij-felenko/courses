#ifndef DC_MOTOR_130_HPP_
#define DC_MOTOR_130_HPP_

#include <cstdint>
#include <algorithm>
#include <cmath>

namespace motion {

/**
 * @brief Режим зупинки колекторного двигуна постійного струму.
 */
enum class StopMode : uint8_t {
    Coast = 0,     ///< Вільний вибіг (Hi-Z): ключі моста розімкнені, ротор сповільнюється виключно механічним тертям
    DynamicBrake   ///< Динамічне гальмування: клеми обмотки якоря закорочені накоротко, гасіння енергії струмом проти-ЕРС
};

/**
 * @brief Стан скінченного автомата керування комутацією H-моста.
 */
enum class DriveState : uint8_t {
    Coast = 0,     ///< Спокій або пасивний вибіг із розімкненими ключами (стан високого імпедансу Hi-Z)
    Braking,       ///< Активне динамічне гальмування із замиканням обох клем двигуна накоротко
    Forward,       ///< Обертання вала вперед (IN1 = ШІМ, IN2 = 0)
    Reverse,       ///< Реверсивне обертання вала (IN1 = 0, IN2 = ШІМ)
    DeadTime       ///< Захисна витримка мертвого часу (усі ключі вимкнені перед зміною активної діагоналі)
};

/**
 * @brief Абстрактний апаратний інтерфейс генерації ШІМ-сигналів і комутації ключів H-моста.
 * Забезпечує повну незалежність логіки драйвера від конкретної периферії мікроконтролера
 * (STM32 TIM, ESP32 MCPWM/LEDC, AVR Timer, Raspberry Pi Pico тощо).
 */
class IHBridgeOutput {
public:
    virtual ~IHBridgeOutput() = default;

    /**
     * @brief Ініціалізація апаратних виводів і каналів таймера ШІМ.
     * @param pin_forward Керуючий вивід або номер каналу ШІМ для напрямку Forward (IN1).
     * @param pin_reverse Керуючий вивід або номер каналу ШІМ для напрямку Reverse (IN2).
     * @param pwm_freq_hz Базова частота ШІМ у герцах.
     * @return true у разі успішного конфігурування периферії, false при апаратній помилці.
     */
    virtual bool init(uint8_t pin_forward, uint8_t pin_reverse, uint32_t pwm_freq_hz) noexcept = 0;

    /**
     * @brief Подача ШІМ для обертання вперед (IN1 = duty_pct, IN2 = 0).
     * @param duty_pct Шпаруватість ШІМ у відсотках [0.0f .. 100.0f].
     */
    virtual void set_forward(float duty_pct) noexcept = 0;

    /**
     * @brief Подача ШІМ для обертання назад (IN1 = 0, IN2 = duty_pct).
     * @param duty_pct Шпаруватість ШІМ у відсотках [0.0f .. 100.0f].
     */
    virtual void set_reverse(float duty_pct) noexcept = 0;

    /**
     * @brief Активне динамічне гальмування — закорочування виводів мотора (IN1 = 1, IN2 = 1).
     * Створює замкнений контур для протікання генераторного струму проти-ЕРС, що гальмує вал.
     */
    virtual void set_dynamic_brake() noexcept = 0;

    /**
     * @brief Пасивний вільний вибіг — розмикання всіх ключів H-моста (IN1 = 0, IN2 = 0).
     * Переводить силовий каскад у стан високого імпедансу (Hi-Z).
     */
    virtual void set_coast() noexcept = 0;
};

/**
 * @brief Структура параметрів конфігурації ШІМ-каналів, захисного мертвого часу та рампінгу.
 */
struct MotorConfig {
    uint8_t pin_forward{9};            ///< Вивід або номер каналу ШІМ для руху вперед (IN1)
    uint8_t pin_reverse{10};           ///< Вивід або номер каналу ШІМ для реверсу (IN2)
    uint32_t pwm_frequency_hz{20000};  ///< Частота ШІМ (20 кГц усуває чутний акустичний писк обмоток двигуна 130)
    uint32_t dead_time_us{50};         ///< Програмна тривалість dead-time (мкс) для виключення наскрізних струмів
    float max_slew_rate_pct_per_s{200.0f}; ///< Темп наростання/спаду швидкості soft-start (% за секунду)
    float min_start_duty_pct{12.0f};   ///< Мінімальна початкова шпаруватість для подолання сухого тертя щіток і редуктора (%)
    StopMode default_stop_mode{StopMode::Coast}; ///< Режим за замовчуванням при досягненні нульової швидкості

    /**
     * @brief Перевірка несуперечливості та безпеки параметрів конфігурації.
     */
    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return (pwm_frequency_hz >= 1000 && pwm_frequency_hz <= 100000) &&
               (dead_time_us >= 1 && dead_time_us <= 50000) &&
               (max_slew_rate_pct_per_s >= 10.0f && max_slew_rate_pct_per_s <= 2000.0f) &&
               (min_start_duty_pct >= 0.0f && min_start_duty_pct <= 50.0f);
    }
};

/**
 * @brief Об'єктно-орієнтований драйвер колекторного двигуна типорозміру 130.
 * 
 * Особливості архітектури:
 * - Безпека комутації (Zero Shoot-Through): обов'язкова програмна витримка dead-time
 *   під час будь-якої зміни напрямку обертання або переходу в стан гальмування.
 * - Неблокувальний рампінг (Soft-Start): лінійне обмеження похідної шпаруватості dD/dt
 *   усуває пускові екстраструми (I_stall до 2.5 А при 3.0 В), запобігає brownout-скиданню МК
 *   та захищає шестерні редуктора від механічного сколювання зубів.
 * - Фізичні режими зупинки: перемикання між вільним вибігом (coast) та швидким гальмуванням проти-ЕРС.
 * - RAII: деструктор гарантовано переводить міст у безпечний стан розімкнених ключів (set_coast).
 * - Повна відсутність динамічного виділення пам'яті (no heap allocation).
 */
class DcMotor130 {
public:
    /**
     * @brief Конструктор привода.
     * @param bridge Посилання на реалізацію апаратного інтерфейсу H-моста.
     * @param config Налаштування каналів, захисного мертвого часу та темпу рампінгу.
     */
    explicit DcMotor130(IHBridgeOutput& bridge, const MotorConfig& config = MotorConfig{}) noexcept;

    /**
     * @brief Деструктор RAII: гарантовано знеструмлює силові ключі моста (Coast / Hi-Z).
     */
    ~DcMotor130() noexcept;

    // Заборона копіювання через пряму прив'язку до фізичного апаратного інтерфейсу
    DcMotor130(const DcMotor130&) = delete;
    DcMotor130& operator=(const DcMotor130&) = delete;

    // Дозвіл семантики переміщення
    DcMotor130(DcMotor130&&) noexcept = default;
    DcMotor130& operator=(DcMotor130&&) noexcept = default;

    /**
     * @brief Ініціалізація апаратного інтерфейсу з передачею параметрів конфігурації.
     * @return true у разі успішної ініціалізації периферії мікроконтролера.
     */
    bool init() noexcept;

    /**
     * @brief Завдання цільової швидкості обертання вала [-100.0% .. +100.0%].
     * Швидкість змінюється плавно завдяки неблокувальному рампінгу soft-start.
     * @param speed_pct Додатні значення — Forward, від'ємні — Reverse, 0.0f — плавна зупинка.
     */
    void set_speed(float speed_pct) noexcept;

    /**
     * @brief Плавна керована зупинка вала за заданим темпом рампи з подальшим утриманням.
     * @param mode Режим зупинки: Coast (вибіг) або DynamicBrake (динамічне гальмування).
     */
    void stop(StopMode mode = StopMode::Coast) noexcept;

    /**
     * @brief Екстрена миттєва зупинка двигуна в обхід темпу наростання (зі збереженням dead-time).
     * @param mode Режим зупинки (за замовчуванням DynamicBrake для найшвидшої зупинки вала).
     * @param now_us Опціональний системний час виклику (мкс) для точного відліку dead-time.
     */
    void emergency_stop(StopMode mode = StopMode::DynamicBrake, uint32_t now_us = 0) noexcept;

    /**
     * @brief Основний неблокувальний крок періодичного оновлення скінченного автомата привода.
     * Викликається у головному суперциклі керування або періодичному таймерному диспетчері.
     * @param current_time_us Поточний системний час у мікросекундах.
     */
    void update(uint32_t current_time_us) noexcept;

    /**
     * @brief Допоміжний виклик оновлення із системним часом у мілісекундах.
     * @param current_time_ms Поточний системний час у мілісекундах.
     */
    void update_ms(uint32_t current_time_ms) noexcept;

    // Геттери поточної телеметрії та стану
    [[nodiscard]] float target_speed() const noexcept { return target_speed_pct_; }
    [[nodiscard]] float current_speed() const noexcept { return current_speed_pct_; }
    [[nodiscard]] float current_duty() const noexcept { return current_duty_pct_; }
    [[nodiscard]] DriveState state() const noexcept { return state_; }
    [[nodiscard]] StopMode active_stop_mode() const noexcept { return active_stop_mode_; }
    [[nodiscard]] bool is_in_dead_time() const noexcept { return state_ == DriveState::DeadTime; }
    [[nodiscard]] bool is_moving() const noexcept { return (state_ == DriveState::Forward || state_ == DriveState::Reverse); }
    [[nodiscard]] const MotorConfig& config() const noexcept { return config_; }

    // Динамічне коригування параметрів
    void set_slew_rate(float pct_per_s) noexcept;
    void set_dead_time_us(uint32_t dead_time_us) noexcept;
    void set_default_stop_mode(StopMode mode) noexcept;

private:
    void enter_dead_time(DriveState next_state, uint32_t now_us) noexcept;

    IHBridgeOutput& bridge_;
    MotorConfig config_;

    float target_speed_pct_{0.0f};   ///< Задана швидкість у відсотках [-100.0f .. +100.0f]
    float current_speed_pct_{0.0f};  ///< Поточна швидкість у відсотках [-100.0f .. +100.0f]
    float current_duty_pct_{0.0f};   ///< Поточна вихідна шпаруватість ШІМ [0.0f .. 100.0f]

    DriveState state_{DriveState::Coast};
    DriveState pending_state_{DriveState::Coast};
    StopMode active_stop_mode_{StopMode::Coast};

    uint32_t last_update_us_{0};
    uint32_t dead_time_start_us_{0};
    bool has_first_tick_{false};
    bool is_initialized_{false};
};

} // namespace motion

#endif // DC_MOTOR_130_HPP_
