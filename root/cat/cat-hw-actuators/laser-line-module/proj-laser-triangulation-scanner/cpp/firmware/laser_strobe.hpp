#define FIRMWARE_LASER_STROBE_HPP_

#include <cstdint>
#include <algorithm>

namespace laser {

/**
 * @brief Режими синхронізації стробування лазерного модуля.
 */
enum class SyncMode : uint8_t {
    InternalTimer = 0,   // Внутрішня періодична генерація стробів таймером МК
    ExternalTrigger = 1  // Зовнішній строб-сигнал (вхід синхронізації від камери)
};

/**
 * @brief Поточний робочий стан контролера стробування.
 */
enum class LaserState : uint8_t {
    Disabled = 0,      // Лазер вимкнено, затвор MOSFET притягнуто до GND
    Standby = 1,       // Очікування імпульсу запуску або синхросигналу
    Strobing = 2,      // Активне генерування строб-імпульсів
    FaultLockout = 3   // Аварійне блокування безпеки (Watchdog / перегрів / збій)
};

/**
 * @brief Причина спрацювання аварійного захисного блокування.
 */
enum class LockoutReason : uint8_t {
    None = 0,                 // Немає аварії
    WatchdogTimeout = 1,      // Втрата зв'язку з хостом (тайм-аут сторожового таймера)
    ExcessivePulseWidth = 2,  // Спроба встановити неприпустимо довгий імпульс
    ExcessiveDutyCycle = 3,   // Перевищення максимального коефіцієнта заповнення (перегрів)
    HardwareFault = 4         // Апаратний збій вихідного каскаду
};

/**
 * @brief Структура конфігурації параметрів стробування лазера.
 */
struct StrobeConfig {
    uint32_t pulse_width_us{200};          // Тривалість імпульсу лазера (експозиція, мкс)
    uint32_t period_us{20000};             // Період стробування (20000 мкс = 50 Гц)
    uint32_t watchdog_timeout_ms{150};     // Граничний час без підтвердження хоста (мс)
    uint32_t max_pulse_width_us{2000};     // Максимально дозволений імпульс (захист діода)
    uint16_t max_duty_cycle_permille{100}; // Максимальний duty cycle у проміле (10.0%)
    SyncMode sync_mode{SyncMode::InternalTimer}; // Режим запуску стробів
};

/**
 * @brief Статистика роботи драйвера стробування лазера.
 */
struct StrobeTelemetry {
    uint32_t total_strobes{0};           // Загальна кількість згенерованих стробів
    uint32_t watchdog_feed_count{0};      // Кількість отриманих скидань сторожового таймера
    uint32_t last_pulse_duration_us{0};   // Фактична тривалість останнього імпульсу
    LaserState current_state{LaserState::Disabled};   // Поточний стан
    LockoutReason lockout_reason{LockoutReason::None}; // Причина блокування
};

/**
 * @brief Низькорівневий інтерфейс керування таймером та GPIO для N-MOSFET ключа.
 * 
 * У реальному мікроконтролері (наприклад STM32 / Cortex-M) ці методи мапляться
 * на регістри таймера (TIMx->ARR, TIMx->CCR1, TIMx->CCER) та регістри GPIO (BSRR/ODR).
 */
class HardwareTimerBackend {
public:
    virtual ~HardwareTimerBackend() = default;

    // Налаштування базової частоти таймера (1 МГц = 1 мкс на тік)
    virtual void configure_timebase(uint32_t prescaler, uint32_t auto_reload) = 0;

    // Встановлення тривалості активного рівня на затворі MOSFET
    virtual void set_compare_value(uint32_t compare_value) = 0;

    // Апаратний дозвіл генерації PWM/One-Pulse на вивід затвора
    virtual void start_strobe_timer() = 0;

    // Апаратне зупинення таймера та примусове притискання затвора MOSFET до нуля
    virtual void stop_strobe_timer() = 0;

    // Пряме апаратне відключення піна (failsafe shutdown)
    virtual void force_gate_low() = 0;
};

/**
 * @brief Контролер синхронізованого стробування лазерного модуля.
 * 
 * Забезпечує мікросекундну генерацію імпульсів N-MOSFET ключа в такт із
 * кадровою синхронізацією камери, моніторить сторожовий таймер хоста
 * та захищає лазерний діод від перегріву і небезпечного випромінювання.
 */
class LaserStrobeController {
public:
    explicit LaserStrobeController(HardwareTimerBackend& timer_backend) noexcept
        : timer_(timer_backend) {}

    /**
     * @brief Ініціалізація апаратних ресурсів. Вивід затвора гарантовано глушиться в 0.
     */
    bool init(const StrobeConfig& config) noexcept {
        timer_.force_gate_low();
        state_ = LaserState::Disabled;
        lockout_reason_ = LockoutReason::None;
        telemetry_ = StrobeTelemetry{};

        return apply_configuration(config);
    }

    /**
     * @brief Оновлення конфігурації із суворою валідацією меж безпеки.
     */
    bool apply_configuration(const StrobeConfig& config) noexcept {
        if (state_ == LaserState::FaultLockout) {
            return false; // Поки активне аварійне блокування, зміна конфігурації заборонена
        }

        // Перевірка 1: Тривалість імпульсу не перевищує апаратний ліміт діода
        if (config.pulse_width_us == 0 || config.pulse_width_us > config.max_pulse_width_us) {
            trigger_lockout(LockoutReason::ExcessivePulseWidth);
            return false;
        }

        // Перевірка 2: Період має бути суворо більшим за імпульс
        if (config.period_us <= config.pulse_width_us) {
            trigger_lockout(LockoutReason::ExcessiveDutyCycle);
            return false;
        }

        // Перевірка 3: Коефіцієнт заповнення (duty cycle) у межах теплового розсіювання діода
        const uint32_t duty_permille = (config.pulse_width_us * 1000UL) / config.period_us;
        if (duty_permille > config.max_duty_cycle_permille) {
            trigger_lockout(LockoutReason::ExcessiveDutyCycle);
            return false;
        }

        config_ = config;

        // Налаштування таймера: крок 1 мкс (при частоті тактування таймера 1 МГц)
        // ARR визначає період повторення стробів, CCR - ширину спалаху
        timer_.configure_timebase(0, config_.period_us);
        timer_.set_compare_value(config_.pulse_width_us);

        return true;
    }

    /**
     * @brief Дозвіл генерації стробування.
     */
    bool enable(uint32_t current_time_ms) noexcept {
        if (state_ == LaserState::FaultLockout) {
            return false;
        }

        last_watchdog_pet_ms_ = current_time_ms;
        state_ = LaserState::Strobing;
        telemetry_.current_state = state_;

        if (config_.sync_mode == SyncMode::InternalTimer) {
            timer_.start_strobe_timer();
        } else {
            // У режимі зовнішнього тригера чекаємо імпульсу від камери
            state_ = LaserState::Standby;
            telemetry_.current_state = state_;
        }

        return true;
    }

    /**
     * @brief Штатне вимкнення лазера.
     */
    void disable() noexcept {
        if (state_ != LaserState::FaultLockout) {
            timer_.stop_strobe_timer();
            timer_.force_gate_low();
            state_ = LaserState::Disabled;
            telemetry_.current_state = state_;
        }
    }

    /**
     * @brief Запуск одиничного стробу (викликається за зовнішнім перериванням від камери).
     */
    void trigger_single_strobe() noexcept {
        if (state_ == LaserState::Standby || state_ == LaserState::Strobing) {
            timer_.start_strobe_timer();
            telemetry_.total_strobes++;
            telemetry_.last_pulse_duration_us = config_.pulse_width_us;
        }
    }

    /**
     * @brief Скидання сторожового таймера (heartbeat від керівного хоста).
     * Якщо хост завис або зупинив захоплення відео, сторожовий таймер вимкне лазер.
     */
    void feed_watchdog(uint32_t current_time_ms) noexcept {
        last_watchdog_pet_ms_ = current_time_ms;
        telemetry_.watchdog_feed_count++;
    }

    /**
     * @brief Періодичний фоновий моніторинг безпеки (викликається в головному циклі).
     */
    void poll_failsafe(uint32_t current_time_ms) noexcept {
        if (state_ == LaserState::Disabled || state_ == LaserState::FaultLockout) {
            return;
        }

        // Перевірка часу від останнього підтвердження життя хоста
        const uint32_t elapsed_ms = current_time_ms - last_watchdog_pet_ms_;
        if (elapsed_ms > config_.watchdog_timeout_ms) {
            trigger_lockout(LockoutReason::WatchdogTimeout);
        }
    }

    /**
     * @brief Скидання аварійного стану блокування після усунення причини.
     */
    bool reset_lockout(uint32_t current_time_ms) noexcept {
        if (state_ != LaserState::FaultLockout) {
            return true;
        }

        timer_.force_gate_low();
        lockout_reason_ = LockoutReason::None;
        state_ = LaserState::Disabled;
        telemetry_.current_state = state_;
        telemetry_.lockout_reason = LockoutReason::None;
        last_watchdog_pet_ms_ = current_time_ms;
        return true;
    }

    [[nodiscard]] LaserState state() const noexcept { return state_; }
    [[nodiscard]] LockoutReason lockout_reason() const noexcept { return lockout_reason_; }
    [[nodiscard]] const StrobeTelemetry& telemetry() const noexcept { return telemetry_; }
    [[nodiscard]] const StrobeConfig& config() const noexcept { return config_; }

private:
    void trigger_lockout(LockoutReason reason) noexcept {
        timer_.stop_strobe_timer();
        timer_.force_gate_low(); // Апаратний затвор у нуль за будь-яких умов

        state_ = LaserState::FaultLockout;
        lockout_reason_ = reason;

        telemetry_.current_state = state_;
        telemetry_.lockout_reason = reason;
    }

    HardwareTimerBackend& timer_;
    StrobeConfig config_{};
    LaserState state_{LaserState::Disabled};
    LockoutReason lockout_reason_{LockoutReason::None};
    uint32_t last_watchdog_pet_ms_{0};
    StrobeTelemetry telemetry_{};
};

} // namespace laser

#endif // FIRMWARE_LASER_STROBE_HPP_\n
