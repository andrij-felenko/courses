#include <cstdint>

/* C++ драйвер прецизійного стробування лазера в режимі One-Pulse Mode */
class LaserStrobeDriver {
public:
    struct TimerRegisters {
        volatile uint32_t CR1;
        volatile uint32_t CR2;
        volatile uint32_t SMCR;
        volatile uint32_t DIER;
        volatile uint32_t SR;
        volatile uint32_t EGR;
        volatile uint32_t CCMR1;
        volatile uint32_t CCMR2;
        volatile uint32_t CCER;
        volatile uint32_t CNT;
        volatile uint32_t PSC;
        volatile uint32_t ARR;
        volatile uint32_t RCR;
        volatile uint32_t CCR[4];
    };

    LaserStrobeDriver(TimerRegisters* timer, uint32_t bus_frequency_hz)
        : timer_(timer), bus_freq_hz_(bus_frequency_hz) {}

    /**
     * @brief Базова конфігурація периферії таймера в режим One-Pulse.
     */
    void init() {
        if (!timer_) {
            return;
        }

        timer_->CR1 = 0;
        timer_->CR2 = 0;
        timer_->SMCR = 0;

        // Поділ частоти для кроку лічильника в 1 мікросекунду
        timer_->PSC = (bus_freq_hz_ / 1000000U) - 1U;

        // Встановлюємо біт OPM (автовимкнення після одного циклу) та ARPE
        timer_->CR1 |= (1U << 3) | (1U << 7);

        // PWM Mode 2 на каналі 1: пауза до CCR1, спалах від CCR1 до ARR
        timer_->CCMR1 &= ~((0x7U << 4) | (0x3U << 0));
        timer_->CCMR1 |= (0x7U << 4) | (1U << 3);

        // Увімкнення прямого виходу каналу 1
        timer_->CCER &= ~(1U << 1);
        timer_->CCER |= (1U << 0);
    }

    /**
     * @brief Задання параметрів стробування.
     * @param delay_us Захисний інтервал перед увімкненням (мкс).
     * @param duration_us Тривалість спалаху лазера (мкс).
     */
    void configure_pulse(uint32_t delay_us, uint32_t duration_us) {
        if (!timer_) {
            return;
        }

        timer_->CCR[0] = delay_us;
        timer_->ARR = delay_us + duration_us;

        // Оновлення регістрів подією оновлення
        timer_->EGR = (1U << 0);
    }

    /**
     * @brief Активація апаратної синхронізації з сигналом затвора камери.
     */
    void enable_camera_hardware_trigger() {
        if (!timer_) {
            return;
        }

        // TS = 101b (Фільтрований вхід TI1FP1), SMS = 110b (Trigger Mode)
        timer_->SMCR &= ~((0x7U << 4) | (0x7U << 0));
        timer_->SMCR |= (0x5U << 4) | (0x6U << 0);
    }

    /**
     * @brief Примусовий одиночний спалах за викликом із коду.
     */
    void trigger_single_pulse() {
        if (!timer_) {
            return;
        }

        timer_->CNT = 0;
        timer_->CR1 |= (1U << 0); // Запуск лічильника CEN
    }

    /**
     * @brief Перевірка, чи активний вихідний імпульс у даний момент.
     */
    bool is_emitting() const {
        if (!timer_) {
            return false;
        }
        // У режимі OPM біт CEN залишається 1, доки триває імпульс
        return (timer_->CR1 & (1U << 0)) != 0;
    }

private:
    TimerRegisters* timer_;
    uint32_t bus_freq_hz_;
};
