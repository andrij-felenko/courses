#include <cstdint>
#include <algorithm>

// Структура конфігурації апаратного таймера ШІМ
struct TimerHwConfig {
    volatile uint32_t* cr1;    // Регістр керування (Control Register 1)
    volatile uint32_t* ccmr1;  // Регістр вибору режиму каналів (Capture/Compare Mode Register 1)
    volatile uint32_t* ccer;   // Регістр дозволу виводу (Capture/Compare Enable Register)
    volatile uint32_t* psc;    // Регістр передподільника (Prescaler)
    volatile uint32_t* arr;    // Регістр автоперезавантаження періоду (Auto-Reload Register)
    volatile uint32_t* ccr1;   // Буферний регістр порівняння каналу 1 (Capture/Compare Register 1)
    volatile uint32_t* egr;    // Регістр генерації подій (Event Generation Register)
};

class LaserPwmController {
public:
    explicit LaserPwmController(const TimerHwConfig& hw)
        : hw_(hw), timer_clock_hz_(0), pwm_frequency_hz_(0), max_ticks_(0) {}

    // Ініціалізація таймера на задану несучу частоту з увімкненням тіньових регістрів
    bool init(uint32_t timer_clock_hz, uint32_t target_pwm_freq_hz) {
        if (timer_clock_hz == 0 || target_pwm_freq_hz == 0 || target_pwm_freq_hz > (timer_clock_hz / 2)) {
            return false;
        }

        timer_clock_hz_ = timer_clock_hz;
        pwm_frequency_hz_ = target_pwm_freq_hz;

        // Використовуємо нульовий дільник для максимальної роздільної здатності
        uint32_t prescaler = 0;
        uint32_t period_ticks = timer_clock_hz_ / ((prescaler + 1) * pwm_frequency_hz_);

        if (period_ticks < 2 || period_ticks > 0x10000) {
            // Вихід за межі 16-бітного таймера або занадто низька дискретність
            return false;
        }

        max_ticks_ = period_ticks;

        // Налаштування регістрів таймера
        *hw_.psc = prescaler;
        *hw_.arr = max_ticks_ - 1;
        *hw_.ccr1 = 0; // Початковий стан: нульова яскравість (лазер вимкнено)

        // Конфігурація каналу 1 у режим PWM Mode 1 (вихід активний, поки CNT < CCR1)
        // Біт OC1PE (біт 3 у CCMR1) активує буфер попереднього завантаження (preload/shadow)
        constexpr uint32_t CCMR1_PWM_MODE1 = (0b110 << 4);
        constexpr uint32_t CCMR1_OC1PE     = (1 << 3);
        *hw_.ccmr1 &= ~0xFFFF;
        *hw_.ccmr1 |= (CCMR1_PWM_MODE1 | CCMR1_OC1PE);

        // Увімкнення виходу каналу 1 (пряма полярність: активний високий рівень)
        constexpr uint32_t CCER_CC1E = (1 << 0);
        *hw_.ccer |= CCER_CC1E;

        // Біт ARPE (біт 7 у CR1) вмикає буферизацію регістра періоду ARR
        constexpr uint32_t CR1_ARPE = (1 << 7);
        constexpr uint32_t CR1_CEN  = (1 << 0);
        *hw_.cr1 |= CR1_ARPE;

        // Примусова генерація події оновлення (UG) для завантаження буферів у робочі тіньові регістри
        constexpr uint32_t EGR_UG = (1 << 0);
        *hw_.egr |= EGR_UG;

        // Запуск лічильника таймера
        *hw_.cr1 |= CR1_CEN;

        return true;
    }

    // Встановлення відносної яскравості у відсотках (діапазон 0.0f .. 100.0f)
    // Оновлює значення безпечно через буфер попереднього завантаження
    void set_brightness_percent(float percent) {
        // Жорстке обмеження допустимого діапазону для запобігання переповнення
        float clamped = std::clamp(percent, 0.0f, 100.0f);
        float duty_ratio = clamped / 100.0f;

        // Обчислення кількості тіків з округленням
        uint32_t compare_ticks = static_cast<uint32_t>((duty_ratio * max_ticks_) + 0.5f);
        if (compare_ticks > max_ticks_) {
            compare_ticks = max_ticks_;
        }

        // Атомарний запис у буферний регістр; апаратура перенесе його в тіньовий регістр на UEV
        *hw_.ccr1 = compare_ticks;
    }

    // Миттєве вимкнення випромінювання на апаратному рівні
    void force_off() {
        *hw_.ccr1 = 0;
    }

    uint32_t get_resolution_steps() const {
        return max_ticks_;
    }

private:
    TimerHwConfig hw_;
    uint32_t timer_clock_hz_;
    uint32_t pwm_frequency_hz_;
    uint32_t max_ticks_;
};
