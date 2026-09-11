#include <cstdint>
#include <atomic>

// Стани автомата драйвера лазерної лінії
enum class LaserState : uint8_t {
    Init,          // Початкова ініціалізація, лазер вимкнено
    Ready,         // Очікування тригера, лазер знеструмлено
    Emitting,      // Активне випромінювання, watchdog активовано
    FaultLockout   // Аварійне блокування, випромінювання заборонено
};

// Причини переходу в аварійне блокування
enum class FaultReason : uint8_t {
    None,
    WatchdogTimeout,  // Зависання конвеєра або перевищення тривалості стробу
    InvalidRequest    // Спроба некоректного переходу
};

// Апаратний інтерфейс низького рівня для керування піном лазера
class ILaserHwOutput {
public:
    virtual void force_laser_off() = 0;
    virtual void enable_laser_output() = 0;
    virtual void start_watchdog_timer(uint32_t timeout_us) = 0;
    virtual void stop_watchdog_timer() = 0;
    virtual void reload_watchdog_timer(uint32_t timeout_us) = 0;
    virtual ~ILaserHwOutput() = default;
};

class LaserSafetyDriver {
public:
    explicit LaserSafetyDriver(ILaserHwOutput& hw, uint32_t default_timeout_us = 20000)
        : hw_(hw),
          state_(LaserState::Init),
          last_fault_(FaultReason::None),
          watchdog_timeout_us_(default_timeout_us) {}

    // Ініціалізація підсистеми безпеки та перехід у стан Ready
    bool init() {
        // Гарантоване фізичне знеструмлення лазера
        hw_.force_laser_off();
        hw_.stop_watchdog_timer();

        last_fault_ = FaultReason::None;
        state_.store(LaserState::Ready, std::memory_order_release);
        return true;
    }

    // Запуск випромінювання (стробу) із заданою тривалістю
    bool start_emission(uint32_t pulse_duration_us) {
        // Дозволено перехід у стан Emitting лише зі стану Ready
        if (state_.load(std::memory_order_acquire) != LaserState::Ready) {
            return false;
        }

        // Робочий таймаут безпеки встановлюємо з невеликим технологічним запасом (+20%),
        // але не більше допустимого максимуму
        uint32_t safety_timeout = pulse_duration_us + (pulse_duration_us / 5) + 1000;
        if (safety_timeout > watchdog_timeout_us_) {
            safety_timeout = watchdog_timeout_us_;
        }

        // Спершу зводимо таймер безпеки, і лише потім відкриваємо силовий ключ
        hw_.start_watchdog_timer(safety_timeout);
        hw_.enable_laser_output();

        state_.store(LaserState::Emitting, std::memory_order_release);
        return true;
    }

    // Штатне вимкнення випромінювання після завершення експозиції
    void stop_emission() {
        LaserState expected = LaserState::Emitting;
        if (state_.compare_exchange_strong(expected, LaserState::Ready,
                                           std::memory_order_acq_rel)) {
            // Апаратне вимкнення виходу та зупинка таймера безпеки
            hw_.force_laser_off();
            hw_.stop_watchdog_timer();
        }
    }

    // Скидання сторожового таймера безпеки («watchdog pet»)
    // Викликається потоком комп'ютерного зору під час тривалої неперервної серії
    bool pet_watchdog() {
        if (state_.load(std::memory_order_acquire) != LaserState::Emitting) {
            return false;
        }

        // Перезавантаження апаратного лічильника безпеки
        hw_.reload_watchdog_timer(watchdog_timeout_us_);
        return true;
    }

    // Обробник переривання сторожового таймера (ISR)
    // Викликається апаратурою при вичерпанні ліміту часу увімкненого стану
    void on_watchdog_isr() {
        // Негайне знеструмлення лазера на фізичному рівні без затримок
        hw_.force_laser_off();
        hw_.stop_watchdog_timer();

        last_fault_ = FaultReason::WatchdogTimeout;
        // Перехід у стан захисного блокування
        state_.store(LaserState::FaultLockout, std::memory_order_release);
    }

    // Явне скидання захисного блокування (failsafe reset)
    // Викликається хостом лише після повної діагностики та перезапуску конвеєра CV
    bool failsafe_reset() {
        if (state_.load(std::memory_order_acquire) != LaserState::FaultLockout) {
            return false;
        }

        // Перевіряємо, що силовий ключ дійсно знеструмлено
        hw_.force_laser_off();
        hw_.stop_watchdog_timer();

        last_fault_ = FaultReason::None;
        // Повернення у стан Ready
        state_.store(LaserState::Ready, std::memory_order_release);
        return true;
    }

    LaserState get_current_state() const {
        return state_.load(std::memory_order_acquire);
    }

    FaultReason get_last_fault() const {
        return last_fault_;
    }

private:
    ILaserHwOutput& hw_;
    std::atomic<LaserState> state_;
    FaultReason last_fault_;
    uint32_t watchdog_timeout_us_;
};
