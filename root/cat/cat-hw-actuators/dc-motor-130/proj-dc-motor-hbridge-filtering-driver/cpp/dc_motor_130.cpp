#include "dc_motor_130.hpp"

namespace motion {

DcMotor130::DcMotor130(IHBridgeOutput& bridge, const MotorConfig& config) noexcept
    : bridge_(bridge),
      config_(config.is_valid() ? config : MotorConfig{}),
      active_stop_mode_(config_.default_stop_mode) {
}

DcMotor130::~DcMotor130() noexcept {
    // Безпечне знеструмлення виходів H-моста при руйнуванні об'єкта драйвера (RAII)
    bridge_.set_coast();
}

bool DcMotor130::init() noexcept {
    is_initialized_ = bridge_.init(config_.pin_forward, config_.pin_reverse, config_.pwm_frequency_hz);
    if (is_initialized_) {
        bridge_.set_coast();
        state_ = DriveState::Coast;
        current_duty_pct_ = 0.0f;
        current_speed_pct_ = 0.0f;
    }
    return is_initialized_;
}

void DcMotor130::set_speed(float speed_pct) noexcept {
    target_speed_pct_ = std::clamp(speed_pct, -100.0f, 100.0f);
    if (std::abs(target_speed_pct_) < 0.01f) {
        target_speed_pct_ = 0.0f;
        active_stop_mode_ = config_.default_stop_mode;
    }
}

void DcMotor130::stop(StopMode mode) noexcept {
    target_speed_pct_ = 0.0f;
    active_stop_mode_ = mode;
}

void DcMotor130::emergency_stop(StopMode mode, uint32_t now_us) noexcept {
    target_speed_pct_ = 0.0f;
    active_stop_mode_ = mode;
    current_duty_pct_ = 0.0f;
    current_speed_pct_ = 0.0f;

    if (mode == StopMode::DynamicBrake) {
        // Навіть при екстреній зупинці необхідна пауза dead-time,
        // якщо до цього були відкриті ключі протилежної діагоналі
        bridge_.set_coast();
        state_ = DriveState::DeadTime;
        pending_state_ = DriveState::Braking;
        dead_time_start_us_ = (now_us != 0) ? now_us : last_update_us_;
    } else {
        state_ = DriveState::Coast;
        bridge_.set_coast();
    }
}

void DcMotor130::set_slew_rate(float pct_per_s) noexcept {
    if (pct_per_s >= 10.0f && pct_per_s <= 2000.0f) {
        config_.max_slew_rate_pct_per_s = pct_per_s;
    }
}

void DcMotor130::set_dead_time_us(uint32_t dead_time_us) noexcept {
    if (dead_time_us >= 1 && dead_time_us <= 50000) {
        config_.dead_time_us = dead_time_us;
    }
}

void DcMotor130::set_default_stop_mode(StopMode mode) noexcept {
    config_.default_stop_mode = mode;
}

void DcMotor130::enter_dead_time(DriveState next_state, uint32_t now_us) noexcept {
    // Негайно розмикаємо всі ключі моста для гарантованого запобігання наскрізному струму
    bridge_.set_coast();
    state_ = DriveState::DeadTime;
    pending_state_ = next_state;
    dead_time_start_us_ = now_us;
    current_duty_pct_ = 0.0f;
    current_speed_pct_ = 0.0f;
}

void DcMotor130::update_ms(uint32_t current_time_ms) noexcept {
    update(current_time_ms * 1000U);
}

void DcMotor130::update(uint32_t current_time_us) noexcept {
    if (!has_first_tick_) {
        last_update_us_ = current_time_us;
        has_first_tick_ = true;
        return;
    }

    uint32_t dt_us = current_time_us - last_update_us_;
    last_update_us_ = current_time_us;

    // Захист від аномальних затримок диспетчера або переповнення 32-бітного таймера
    if (dt_us > 1000000U) {
        dt_us = 100000U;
    }
    const float dt_s = static_cast<float>(dt_us) / 1000000.0f;
    const float max_step = config_.max_slew_rate_pct_per_s * dt_s;

    // 1. Стан мертвого часу (Dead-Time)
    // Усі ключі розімкнені; очікуємо повного закриття транзисторів попередньої діагоналі
    if (state_ == DriveState::DeadTime) {
        if ((current_time_us - dead_time_start_us_) >= config_.dead_time_us) {
            state_ = pending_state_;
            current_duty_pct_ = 0.0f;

            if (state_ == DriveState::Forward) {
                // Плавний пуск вперед: під час старту з нуля долаємо сухе тертя щіток і редуктора
                if (config_.min_start_duty_pct > 0.0f && target_speed_pct_ >= config_.min_start_duty_pct) {
                    current_duty_pct_ = config_.min_start_duty_pct;
                }
                current_speed_pct_ = current_duty_pct_;
                bridge_.set_forward(current_duty_pct_);
            } else if (state_ == DriveState::Reverse) {
                // Плавний пуск назад: подолання мертвої зони тертя
                if (config_.min_start_duty_pct > 0.0f && (-target_speed_pct_) >= config_.min_start_duty_pct) {
                    current_duty_pct_ = config_.min_start_duty_pct;
                }
                current_speed_pct_ = -current_duty_pct_;
                bridge_.set_reverse(current_duty_pct_);
            } else if (state_ == DriveState::Braking) {
                current_speed_pct_ = 0.0f;
                bridge_.set_dynamic_brake();
            } else {
                state_ = DriveState::Coast;
                current_speed_pct_ = 0.0f;
                bridge_.set_coast();
            }
        }
        return;
    }

    // 2. Стани спокою (Coast або Braking)
    if (state_ == DriveState::Coast || state_ == DriveState::Braking) {
        if (target_speed_pct_ > 0.0f) {
            // Перехід у Forward через обов'язковий dead-time (критично при виході з Braking!)
            enter_dead_time(DriveState::Forward, current_time_us);
        } else if (target_speed_pct_ < 0.0f) {
            // Перехід у Reverse через dead-time
            enter_dead_time(DriveState::Reverse, current_time_us);
        } else {
            current_duty_pct_ = 0.0f;
            current_speed_pct_ = 0.0f;
        }
        return;
    }

    // 3. Стан обертання вперед (Forward)
    if (state_ == DriveState::Forward) {
        if (target_speed_pct_ > 0.0f) {
            // Лінійне регулювання темпу зміни шпаруватості (Soft-Start рампінг dD/dt)
            const float target_duty = target_speed_pct_;
            if (current_duty_pct_ < target_duty) {
                current_duty_pct_ = std::min(target_duty, current_duty_pct_ + max_step);
            } else if (current_duty_pct_ > target_duty) {
                current_duty_pct_ = std::max(target_duty, current_duty_pct_ - max_step);
            }
            current_speed_pct_ = current_duty_pct_;
            bridge_.set_forward(current_duty_pct_);
        } else {
            // Гальмування до нульової швидкості за темпом рампи
            current_duty_pct_ = std::max(0.0f, current_duty_pct_ - max_step);
            current_speed_pct_ = current_duty_pct_;
            bridge_.set_forward(current_duty_pct_);

            if (current_duty_pct_ <= 0.001f) {
                current_duty_pct_ = 0.0f;
                current_speed_pct_ = 0.0f;

                if (target_speed_pct_ < 0.0f) {
                    // Контрольований реверс: спочатку спад до 0, потім dead-time перед комутацією
                    enter_dead_time(DriveState::Reverse, current_time_us);
                } else {
                    // Повна плавна зупинка: перехід у вибраний режим утримання
                    if (active_stop_mode_ == StopMode::DynamicBrake) {
                        enter_dead_time(DriveState::Braking, current_time_us);
                    } else {
                        state_ = DriveState::Coast;
                        bridge_.set_coast();
                    }
                }
            }
        }
        return;
    }

    // 4. Стан реверсивного обертання (Reverse)
    if (state_ == DriveState::Reverse) {
        if (target_speed_pct_ < 0.0f) {
            // Плавне відстеження цільової реверсивної швидкості
            const float target_duty = -target_speed_pct_;
            if (current_duty_pct_ < target_duty) {
                current_duty_pct_ = std::min(target_duty, current_duty_pct_ + max_step);
            } else if (current_duty_pct_ > target_duty) {
                current_duty_pct_ = std::max(target_duty, current_duty_pct_ - max_step);
            }
            current_speed_pct_ = -current_duty_pct_;
            bridge_.set_reverse(current_duty_pct_);
        } else {
            // Сповільнення реверсу до нульової швидкості
            current_duty_pct_ = std::max(0.0f, current_duty_pct_ - max_step);
            current_speed_pct_ = -current_duty_pct_;
            bridge_.set_reverse(current_duty_pct_);

            if (current_duty_pct_ <= 0.001f) {
                current_duty_pct_ = 0.0f;
                current_speed_pct_ = 0.0f;

                if (target_speed_pct_ > 0.0f) {
                    // Перехід у Forward після досягнення нуля та витримки dead-time
                    enter_dead_time(DriveState::Forward, current_time_us);
                } else {
                    // Зупинка реверсу
                    if (active_stop_mode_ == StopMode::DynamicBrake) {
                        enter_dead_time(DriveState::Braking, current_time_us);
                    } else {
                        state_ = DriveState::Coast;
                        bridge_.set_coast();
                    }
                }
            }
        }
        return;
    }
}

} // namespace motion
