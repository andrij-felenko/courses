// laser_line_driver.cpp
#include "laser_line_driver.hpp"

namespace Laser {

LaserLineDriver::LaserLineDriver(ILaserHal& hal, uint32_t max_allowed_strobe_us)
    : hal_(hal),
      max_strobe_us_(max_allowed_strobe_us),
      pwm_freq_hz_(30000),
      current_brightness_(0.0f),
      state_(State::Init),
      errors_(Error::None) {}

bool LaserLineDriver::init(uint32_t pwm_frequency_hz) {
    pwm_freq_hz_ = pwm_frequency_hz;

    // Гарантоване фізичне вимкнення виводу
    hal_.set_pin_state(false);
    hal_.enable_pwm_output(false);
    hal_.cancel_strobe_timer();
    hal_.cancel_watchdog_timer();

    // Налаштування ШІМ на 30 кГц з початковою нульовою яскравістю
    hal_.configure_pwm(pwm_freq_hz_, 0.0f);

    errors_.store(Error::None, std::memory_order_release);
    state_.store(State::Ready, std::memory_order_release);
    return true;
}

void LaserLineDriver::set_optical_parameters(float brightness_percent) {
    current_brightness_ = std::clamp(brightness_percent, 0.0f, 100.0f);
    // Буферизоване оновлення регістра порівняння через HAL
    hal_.configure_pwm(pwm_freq_hz_, current_brightness_);
}

bool LaserLineDriver::trigger_strobe_async(uint32_t strobe_duration_us) {
    // Перевірка допустимості тривалості стробу
    if (strobe_duration_us == 0 || strobe_duration_us > max_strobe_us_) {
        enter_fault_lockout(Error::SyncLost);
        return false;
    }

    // Дозволено запуск лише зі стану Ready
    State expected = State::Ready;
    if (!state_.compare_exchange_strong(expected, State::Emitting,
                                        std::memory_order_acq_rel)) {
        return false;
    }

    // Зводимо сторожовий таймер із запасом +20% (мінімум +500 мкс)
    uint32_t wd_timeout = strobe_duration_us + (strobe_duration_us / 5) + 500;
    hal_.arm_watchdog_timer(wd_timeout);

    // Налаштовуємо апаратний таймер тривалості стробу
    hal_.arm_strobe_timer(strobe_duration_us);

    // Відкриваємо апаратний вихід ШІМ
    hal_.enable_pwm_output(true);

    return true;
}

void LaserLineDriver::cancel_strobe() {
    State expected = State::Emitting;
    if (state_.compare_exchange_strong(expected, State::Ready,
                                        std::memory_order_acq_rel)) {
        hal_.enable_pwm_output(false);
        hal_.cancel_strobe_timer();
        hal_.cancel_watchdog_timer();
    }
}

void LaserLineDriver::pet_safety_watchdog() {
    if (state_.load(std::memory_order_acquire) == State::Emitting) {
        // Перезавантаження апаратного лічильника безпеки
        hal_.reload_watchdog_timer(max_strobe_us_ + 1000);
    }
}

void LaserLineDriver::on_strobe_timer_isr() {
    // Апаратне вимкнення за завершенням запланованого стробу кадру
    hal_.enable_pwm_output(false);
    hal_.cancel_watchdog_timer();

    State expected = State::Emitting;
    state_.compare_exchange_strong(expected, State::Ready,
                                   std::memory_order_acq_rel);
}

void LaserLineDriver::on_watchdog_timeout_isr() {
    // Спрацювання захисту: потік завис або строб перевищив ліміт
    enter_fault_lockout(Error::WatchdogTimeout);
}

void LaserLineDriver::report_hardware_fault(uint32_t error_flag) {
    enter_fault_lockout(error_flag);
}

void LaserLineDriver::enter_fault_lockout(uint32_t error_flag) {
    // Миттєве апаратне знеструмлення
    hal_.enable_pwm_output(false);
    hal_.set_pin_state(false);
    hal_.cancel_strobe_timer();
    hal_.cancel_watchdog_timer();

    errors_.fetch_or(error_flag, std::memory_order_release);
    state_.store(State::FaultLockout, std::memory_order_release);
}

bool LaserLineDriver::failsafe_reset() {
    if (state_.load(std::memory_order_acquire) != State::FaultLockout) {
        return false;
    }

    // Фізична перевірка безпеки: переконуємося у знеструмленні
    hal_.enable_pwm_output(false);
    hal_.set_pin_state(false);

    errors_.store(Error::None, std::memory_order_release);
    state_.store(State::Ready, std::memory_order_release);
    return true;
}

State LaserLineDriver::get_state() const {
    return state_.load(std::memory_order_acquire);
}

uint32_t LaserLineDriver::get_error_code() const {
    return errors_.load(std::memory_order_acquire);
}

bool LaserLineDriver::is_locked() const {
    return state_.load(std::memory_order_acquire) == State::FaultLockout;
}

} // namespace Laser
