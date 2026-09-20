#include "continuous_rotation_servo.hpp"

namespace motion {

ContinuousRotationServo::ContinuousRotationServo(
    IPwmOutput& pwm,
    const ServoCalibration& cal,
    float max_accel_pct_per_s,
    uint32_t reverse_dwell_ms
) noexcept
    : pwm_(pwm),
      cal_(cal.is_valid() ? cal : ServoCalibration{}),
      max_accel_pct_per_s_(max_accel_pct_per_s > 0.1f ? max_accel_pct_per_s : 200.0f),
      reverse_dwell_ms_(reverse_dwell_ms),
      current_pulse_us_(cal_.neutral_us),
      state_(DriveState::Detached),
      is_attached_(false) {
}

void ContinuousRotationServo::set_speed(float speed_percent) noexcept {
    // Безпечне відсікання вхідної команди до допустимого діапазону [-100.0% .. +100.0%]
    target_speed_pct_ = std::clamp(speed_percent, -100.0f, 100.0f);
}

uint16_t ContinuousRotationServo::speed_to_pulse(float speed_pct) const noexcept {
    // Враховуємо апаратну або програмну інверсію напрямку обертання
    float effective_speed = cal_.inverted ? -speed_pct : speed_pct;
    effective_speed = std::clamp(effective_speed, -100.0f, 100.0f);

    // Якщо швидкість дорівнює нулю або перебуває в межах числової похибки,
    // повертаємо точне значення каліброваної нейтральної точки спокою.
    // Це поміщає сигнал суворо в середину апаратної мертвої зони внутрішнього компаратора серва.
    constexpr float kSpeedEpsilon = 0.05f;
    if (std::abs(effective_speed) < kSpeedEpsilon) {
        return cal_.neutral_us;
    }

    if (effective_speed > 0.0f) {
        // Прямий напрямок обертання (рух вперед):
        // Одразу переступаємо напівширину мертвої зони deadband_us, щоб виключити затримку рушання,
        // та лінійно інтерполюємо діапазон швидкості (0%..100%] до інтервалу [(neutral + deadband) .. max_pulse].
        const float alpha = effective_speed / 100.0f;
        const float base_pulse = static_cast<float>(cal_.neutral_us + cal_.deadband_us);
        const float span = static_cast<float>(cal_.max_pulse_us) - base_pulse;
        const float calculated_pulse = base_pulse + (alpha * span);

        const float clamped_pulse = std::clamp(
            calculated_pulse,
            base_pulse,
            static_cast<float>(cal_.max_pulse_us)
        );
        return static_cast<uint16_t>(std::round(clamped_pulse));
    } else {
        // Зворотний напрямок обертання (реверс):
        // Аналогічно переступаємо нижню межу мертвої зони (neutral - deadband_us) у бік зменшення імпульсу
        // та лінійно інтерполюємо [-100%..0%) до інтервалу [min_pulse .. (neutral - deadband)].
        const float alpha = (-effective_speed) / 100.0f;
        const float base_pulse = static_cast<float>(cal_.neutral_us - cal_.deadband_us);
        const float span = base_pulse - static_cast<float>(cal_.min_pulse_us);
        const float calculated_pulse = base_pulse - (alpha * span);

        const float clamped_pulse = std::clamp(
            calculated_pulse,
            static_cast<float>(cal_.min_pulse_us),
            base_pulse
        );
        return static_cast<uint16_t>(std::round(clamped_pulse));
    }
}

void ContinuousRotationServo::update(uint32_t current_time_ms) noexcept {
    // Якщо привід знеструмлено, обчислення динаміки руху пропускаються
    if (!is_attached_) {
        return;
    }

    // Перша ініціалізація відліку часу
    if (last_update_ms_ == 0) {
        last_update_ms_ = current_time_ms;
        return;
    }

    // Розрахунок дискретного кроку часу dt
    uint32_t dt_ms = current_time_ms - last_update_ms_;
    if (dt_ms == 0) {
        return; // Крок ще не настав у поточному кванті часу
    }

    // Обмеження максимального dt для захисту від сплеску прискорення після довгих пауз
    constexpr uint32_t kMaxDtMs = 100;
    if (dt_ms > kMaxDtMs) {
        dt_ms = kMaxDtMs;
    }
    last_update_ms_ = current_time_ms;
    const float dt_s = static_cast<float>(dt_ms) / 1000.0f;

    // Стан захисної витримки на нульовій швидкості під час зміни знака напрямку (реверсу)
    if (state_ == DriveState::ReversingDwell) {
        current_speed_pct_ = 0.0f;
        apply_pulse(cal_.neutral_us);

        // Перевіряємо, чи минув захисний інтервал для заспокоєння механіки редуктора
        if (current_time_ms - dwell_start_ms_ >= reverse_dwell_ms_) {
            // Витримку завершено: дозволяємо подальший розгін у зворотному напрямку
            state_ = (std::abs(target_speed_pct_) < 0.05f) ? DriveState::Stopped : DriveState::Running;
        } else {
            return; // Залишаємось у стані витримки
        }
    }

    // Визначаємо, чи потрібен безпечний реверс через нуль:
    // якщо поточна швидкість та цільова швидкість мають протилежні знаки.
    constexpr float kZeroThreshold = 0.05f;
    const bool current_moving_forward = (current_speed_pct_ > kZeroThreshold);
    const bool current_moving_backward = (current_speed_pct_ < -kZeroThreshold);
    const bool target_wants_forward = (target_speed_pct_ > kZeroThreshold);
    const bool target_wants_backward = (target_speed_pct_ < -kZeroThreshold);

    const bool requires_reversal =
        (current_moving_forward && target_wants_backward) ||
        (current_moving_backward && target_wants_forward);

    // Максимальна зміна швидкості за поточний крок інтегрування: Δv = a_max * dt
    const float max_delta = max_accel_pct_per_s_ * dt_s;

    if (requires_reversal) {
        // ПРИМУСОВЕ ГАЛЬМУВАННЯ ДО ПОВНОЇ ЗУПИНКИ ПЕРЕД РЕВЕРСОМ:
        // Ми не переходимо одразу в протилежний знак. Спочатку привід сповільнюється строго до 0.
        if (current_speed_pct_ > 0.0f) {
            current_speed_pct_ -= max_delta;
            if (current_speed_pct_ <= 0.0f) {
                current_speed_pct_ = 0.0f;
                state_ = DriveState::ReversingDwell;
                dwell_start_ms_ = current_time_ms;
                apply_pulse(cal_.neutral_us);
                return;
            }
        } else {
            current_speed_pct_ += max_delta;
            if (current_speed_pct_ >= 0.0f) {
                current_speed_pct_ = 0.0f;
                state_ = DriveState::ReversingDwell;
                dwell_start_ms_ = current_time_ms;
                apply_pulse(cal_.neutral_us);
                return;
            }
        }

        // Оновлюємо імпульс гальмування
        state_ = DriveState::Running;
        apply_pulse(speed_to_pulse(current_speed_pct_));
        return;
    }

    // Звичайний лінійний рампінг до цільової швидкості (односпрямований розгін або плавна зупинка)
    const float speed_error = target_speed_pct_ - current_speed_pct_;

    if (std::abs(speed_error) <= max_delta) {
        current_speed_pct_ = target_speed_pct_;
    } else {
        current_speed_pct_ += (speed_error > 0.0f) ? max_delta : -max_delta;
    }

    // Оновлення стану драйвера
    if (std::abs(current_speed_pct_) < kZeroThreshold) {
        current_speed_pct_ = 0.0f;
        state_ = DriveState::Stopped;
    } else {
        state_ = DriveState::Running;
    }

    apply_pulse(speed_to_pulse(current_speed_pct_));
}

void ContinuousRotationServo::detach() noexcept {
    if (is_attached_) {
        pwm_.disable();
        is_attached_ = false;
        state_ = DriveState::Detached;
    }
}

void ContinuousRotationServo::attach() noexcept {
    if (!is_attached_) {
        pwm_.enable();
        is_attached_ = true;
        state_ = (std::abs(current_speed_pct_) < 0.05f) ? DriveState::Stopped : DriveState::Running;
        last_update_ms_ = 0; // Скидаємо мітку часу для коректного першого кроку dt
        apply_pulse(speed_to_pulse(current_speed_pct_));
    }
}

void ContinuousRotationServo::stop_immediately() noexcept {
    target_speed_pct_ = 0.0f;
    current_speed_pct_ = 0.0f;
    state_ = is_attached_ ? DriveState::Stopped : DriveState::Detached;
    apply_pulse(cal_.neutral_us);
}

void ContinuousRotationServo::set_acceleration(float max_accel_pct_per_s) noexcept {
    if (max_accel_pct_per_s > 0.1f) {
        max_accel_pct_per_s_ = max_accel_pct_per_s;
    }
}

bool ContinuousRotationServo::set_calibration(const ServoCalibration& cal) noexcept {
    if (!cal.is_valid()) {
        return false;
    }
    cal_ = cal;
    if (is_attached_) {
        apply_pulse(speed_to_pulse(current_speed_pct_));
    }
    return true;
}

void ContinuousRotationServo::set_reverse_dwell_ms(uint32_t dwell_ms) noexcept {
    reverse_dwell_ms_ = dwell_ms;
}

void ContinuousRotationServo::apply_pulse(uint16_t pulse_us) noexcept {
    current_pulse_us_ = pulse_us;
    if (is_attached_) {
        pwm_.write_pulse_us(pulse_us);
    }
}

} // namespace motion
