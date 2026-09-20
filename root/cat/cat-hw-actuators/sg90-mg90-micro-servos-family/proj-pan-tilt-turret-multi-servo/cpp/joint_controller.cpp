#include "joint_controller.hpp"

#include <algorithm>
#include <cmath>

namespace actuator {

// =============================================================================
// Реалізація класу JointActuator
// =============================================================================

JointActuator::JointActuator(const ActuatorConfig& config)
    : config_(config) {
    // Гарантуємо валідність діапазонів конфігурації
    if (config_.max_angle_deg <= config_.min_angle_deg) {
        config_.max_angle_deg = config_.min_angle_deg + 180.0f;
    }
    if (config_.max_pulse_us <= config_.min_pulse_us) {
        config_.min_pulse_us = 500;
        config_.max_pulse_us = 2500;
    }
    if (config_.max_velocity_deg_s <= 0.0f) {
        config_.max_velocity_deg_s = 120.0f;
    }
}

JointActuator::~JointActuator() {
    // Безпечне відключення: знімаємо керувальний імпульс при руйнуванні об'єкта
    disable();
}

void JointActuator::setPwmSink(PwmWriteCallback callback, void* user_data) noexcept {
    pwm_sink_ = callback;
    pwm_user_data_ = user_data;
}

bool JointActuator::init(float initial_angle_deg, uint32_t current_time_ms) {
    target_angle_deg_ = std::clamp(initial_angle_deg, config_.min_angle_deg, config_.max_angle_deg);
    current_angle_deg_ = target_angle_deg_;
    last_update_ms_ = current_time_ms;
    is_enabled_ = true;
    state_ = ActuatorState::Idle;

    // Початкове позиціювання вала
    sendPulse(calculatePulseWidthUs(current_angle_deg_));
    return true;
}

bool JointActuator::setTargetAngle(float angle_deg) {
    // Якщо привід перебуває в аварійній зупинці, блокуємо нові команди до явного скидання
    if (state_ == ActuatorState::EmergencyStopped) {
        return false;
    }

    target_angle_deg_ = std::clamp(angle_deg, config_.min_angle_deg, config_.max_angle_deg);

    // Якщо поточний кут відрізняється від нового цільового, починаємо рух
    if (std::abs(target_angle_deg_ - current_angle_deg_) > 0.1f) {
        state_ = ActuatorState::Moving;
    }
    return true;
}

void JointActuator::applyCompliance(float retreat_direction) {
    // Адаптивне кутове поступлення: відступаємо на compliance_step_deg проти напрямку опору.
    // Це знімає статичне зусилля з зубців шестерень SG90/MG90S, рятуючи їх від злизування.
    const float direction = (retreat_direction >= 0.0f) ? 1.0f : -1.0f;
    const float new_angle = std::clamp(
        current_angle_deg_ + (direction * config_.compliance_step_deg),
        config_.min_angle_deg,
        config_.max_angle_deg
    );

    current_angle_deg_ = new_angle;
    target_angle_deg_ = new_angle;
    state_ = ActuatorState::Compliant;

    // Негайно оновлюємо імпульс ШІМ для фізичного зняття навантаження
    sendPulse(calculatePulseWidthUs(current_angle_deg_));
}

void JointActuator::emergencyStop() {
    state_ = ActuatorState::EmergencyStopped;
    is_enabled_ = false;
    // Надсилаємо імпульс 0 мкс: апаратний таймер вимикає генерацію,
    // внутрішня схема сервопривода знеструмлює двигун, знімаючи утримувальний момент
    sendPulse(0);
}

void JointActuator::enable() {
    if (state_ == ActuatorState::EmergencyStopped) {
        return;
    }
    is_enabled_ = true;
    state_ = ActuatorState::Idle;
    sendPulse(calculatePulseWidthUs(current_angle_deg_));
}

void JointActuator::disable() {
    is_enabled_ = false;
    if (state_ != ActuatorState::EmergencyStopped) {
        state_ = ActuatorState::Disabled;
    }
    sendPulse(0);
}

void JointActuator::resetFault(uint32_t current_time_ms) {
    last_update_ms_ = current_time_ms;
    is_enabled_ = true;
    state_ = ActuatorState::Idle;
    sendPulse(calculatePulseWidthUs(current_angle_deg_));
}

void JointActuator::update(uint32_t current_time_ms) {
    if (!is_enabled_ || state_ == ActuatorState::EmergencyStopped) {
        return;
    }

    const uint32_t elapsed_ms = current_time_ms - last_update_ms_;
    if (elapsed_ms == 0) {
        return;
    }
    last_update_ms_ = current_time_ms;

    const float angle_error = target_angle_deg_ - current_angle_deg_;
    const float abs_error = std::abs(angle_error);

    // Зона нечутливості позиціювання
    if (abs_error <= 0.05f) {
        current_angle_deg_ = target_angle_deg_;
        if (state_ == ActuatorState::Moving) {
            state_ = ActuatorState::Idle;
        }
        return;
    }

    // Траєкторне профілювання: обмежуємо кутовий крок згідно з допустимою швидкістю,
    // щоб усунути різкі ривки та ударні навантаження на тендітні пластикові або латунні шестерні
    const float max_step = config_.max_velocity_deg_s * (static_cast<float>(elapsed_ms) / 1000.0f);

    if (abs_error <= max_step) {
        current_angle_deg_ = target_angle_deg_;
        state_ = ActuatorState::Idle;
    } else {
        current_angle_deg_ += (angle_error > 0.0f) ? max_step : -max_step;
        state_ = ActuatorState::Moving;
    }

    sendPulse(calculatePulseWidthUs(current_angle_deg_));
}

uint16_t JointActuator::calculatePulseWidthUs(float angle_deg) const noexcept {
    const float clamped_angle = std::clamp(angle_deg, config_.min_angle_deg, config_.max_angle_deg);
    const float angle_span = config_.max_angle_deg - config_.min_angle_deg;
    if (angle_span <= 0.0f) {
        return config_.min_pulse_us;
    }

    const float normalized = (clamped_angle - config_.min_angle_deg) / angle_span;
    const float pulse_span = static_cast<float>(config_.max_pulse_us - config_.min_pulse_us);
    return static_cast<uint16_t>(config_.min_pulse_us + (normalized * pulse_span) + 0.5f);
}

void JointActuator::sendPulse(uint16_t pulse_us) noexcept {
    if (pwm_sink_ != nullptr) {
        pwm_sink_(pulse_us, pwm_user_data_);
    }
}

// =============================================================================
// Реалізація класу JointCurrentMonitor
// =============================================================================

JointCurrentMonitor::JointCurrentMonitor(const CurrentMonitorConfig& config)
    : config_(config) {
    if (config_.filter_alpha <= 0.0f || config_.filter_alpha > 1.0f) {
        config_.filter_alpha = 0.25f;
    }
    if (config_.stall_timeout_ms == 0) {
        config_.stall_timeout_ms = 250;
    }
}

void JointCurrentMonitor::setStallCallback(StallFaultCallback callback, void* user_data) noexcept {
    stall_callback_ = callback;
    stall_user_data_ = user_data;
}

bool JointCurrentMonitor::calibrateZeroOffset(std::span<const uint32_t> zero_samples) {
    if (zero_samples.empty()) {
        return false;
    }

    uint64_t sum = 0;
    for (const uint32_t sample : zero_samples) {
        sum += sample;
    }

    // Програмне усереднення апаратного зміщення струмового датчика у стані спокою
    zero_offset_ma_ = static_cast<float>(sum) / static_cast<float>(zero_samples.size());
    filtered_current_ma_ = 0.0f;
    is_calibrated_ = true;
    return true;
}

void JointCurrentMonitor::notifyMotionStarted(uint32_t current_time_ms) noexcept {
    motion_start_ms_ = current_time_ms;
    in_blanking_window_ = true;
    overcurrent_start_ms_ = 0;
}

void JointCurrentMonitor::update(uint32_t raw_current_ma, uint32_t current_time_ms) {
    // Віднімання апаратного зміщення нуля
    const float raw_val = static_cast<float>(raw_current_ma);
    const float net_current = (raw_val > zero_offset_ma_) ? (raw_val - zero_offset_ma_) : 0.0f;

    // Цифровий експоненційний фільтр низьких частот (EMA)
    filtered_current_ma_ = (config_.filter_alpha * net_current) +
                           ((1.0f - config_.filter_alpha) * filtered_current_ma_);

    // Відсікання пускового струмового сплеску (inrush current blanking):
    // При рушанні нерухомого якоря мікромотора виникає короткий сплеск споживання,
    // який не свідчить про аварійне заклинювання.
    if (in_blanking_window_) {
        if ((current_time_ms - motion_start_ms_) >= config_.blanking_time_ms) {
            in_blanking_window_ = false;
        } else {
            return;
        }
    }

    const uint32_t current_val = static_cast<uint32_t>(filtered_current_ma_ + 0.5f);

    // Аналіз перевищення порогу блокування вала
    if (current_val >= config_.stall_current_ma) {
        if (overcurrent_start_ms_ == 0) {
            overcurrent_start_ms_ = current_time_ms;
        } else if ((current_time_ms - overcurrent_start_ms_) >= config_.stall_timeout_ms) {
            if (current_fault_ != FaultState::StallDetected) {
                current_fault_ = FaultState::StallDetected;
                if (stall_callback_ != nullptr) {
                    stall_callback_(FaultState::StallDetected, current_val, stall_user_data_);
                }
            }
        } else {
            if (current_fault_ != FaultState::StallDetected) {
                current_fault_ = FaultState::Warning;
            }
        }
    } else {
        overcurrent_start_ms_ = 0;
        if (current_fault_ != FaultState::StallDetected) {
            if (current_val >= config_.warning_current_ma) {
                current_fault_ = FaultState::Warning;
            } else {
                current_fault_ = FaultState::Normal;
            }
        }
    }
}

void JointCurrentMonitor::resetFault() noexcept {
    current_fault_ = FaultState::Normal;
    overcurrent_start_ms_ = 0;
    in_blanking_window_ = false;
}

} // namespace actuator
