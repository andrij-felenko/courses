#include "pan_tilt_driver.hpp"

namespace actuators {

PanTiltDriver::PanTiltDriver(const ServoConfig& pan_cfg, const ServoConfig& tilt_cfg, PwmWriteCallback pwm_cb)
    : pwm_cb_(pwm_cb) {
    configs_[static_cast<size_t>(AxisId::PAN)] = pan_cfg;
    configs_[static_cast<size_t>(AxisId::TILT)] = tilt_cfg;
}

void PanTiltDriver::init(uint64_t current_time_us) {
    for (size_t i = 0; i < 2; ++i) {
        auto& state = states_[i];
        const auto& cfg = configs_[i];

        state.current_angle_deg = 90.0f;
        state.start_angle_deg = 90.0f;
        state.target_angle_deg = 90.0f;
        state.start_time_us = current_time_us;
        state.duration_us = 0;
        state.in_motion = false;
        state.last_direction = Direction::STOPPED;

        // Початкове позиціонування у нейтральну точку 90 градусів
        state.last_pulse_us = angleToPulseUs(cfg, state.current_angle_deg);
        if (pwm_cb_) {
            pwm_cb_(cfg.pin, state.last_pulse_us);
        }
    }
}

bool PanTiltDriver::setTarget(AxisId axis, float target_deg, float speed_deg_s, uint64_t current_time_us) {
    const size_t idx = static_cast<size_t>(axis);
    const auto& cfg = configs_[idx];
    auto& state = states_[idx];

    // Захист від ударів: програмні кінцевики soft-limits
    const float clamped_target = std::clamp(target_deg, cfg.min_angle_deg, cfg.max_angle_deg);

    // Якщо привід вже знаходиться у цільовій позиції, рух не потрібен
    const float delta_deg = std::abs(clamped_target - state.current_angle_deg);
    if (delta_deg < 0.05f) {
        state.target_angle_deg = clamped_target;
        state.in_motion = false;
        return true;
    }

    // Визначення робочої кутової швидкості
    const float effective_speed = (speed_deg_s > 0.0f) ? speed_deg_s : cfg.default_speed_deg_s;

    // Розрахунок тривалості сегмента траєкторії: t = delta / speed (у мікросекундах)
    const float duration_sec = delta_deg / effective_speed;
    state.duration_us = static_cast<uint64_t>(duration_sec * 1000000.0f);

    state.start_angle_deg = state.current_angle_deg;
    state.target_angle_deg = clamped_target;
    state.start_time_us = current_time_us;
    state.in_motion = true;

    return true;
}

bool PanTiltDriver::setTargetPanTilt(float pan_deg, float tilt_deg, float speed_deg_s, uint64_t current_time_us) {
    const bool ok_pan = setTarget(AxisId::PAN, pan_deg, speed_deg_s, current_time_us);
    const bool ok_tilt = setTarget(AxisId::TILT, tilt_deg, speed_deg_s, current_time_us);
    return ok_pan && ok_tilt;
}

void PanTiltDriver::update(uint64_t current_time_us) {
    updateAxis(AxisId::PAN, current_time_us);
    updateAxis(AxisId::TILT, current_time_us);
}

void PanTiltDriver::updateAxis(AxisId axis, uint64_t current_time_us) {
    const size_t idx = static_cast<size_t>(axis);
    auto& state = states_[idx];
    const auto& cfg = configs_[idx];

    if (!state.in_motion) {
        return;
    }

    if (state.duration_us == 0 || current_time_us <= state.start_time_us) {
        state.current_angle_deg = state.target_angle_deg;
        state.in_motion = false;
        return;
    }

    const uint64_t elapsed_us = current_time_us - state.start_time_us;

    if (elapsed_us >= state.duration_us) {
        // Досягнуто кінця траєкторії
        state.current_angle_deg = state.target_angle_deg;
        state.in_motion = false;
    } else {
        // Нормалізований час від 0.0 до 1.0
        const float t = static_cast<float>(elapsed_us) / static_cast<float>(state.duration_us);

        // Обчислення коефіцієнта S-кривої (smootherstep)
        const float s = smootherstep(t);

        // Інтерполяція поточної кутової координати
        state.current_angle_deg = state.start_angle_deg + (state.target_angle_deg - state.start_angle_deg) * s;
    }

    // Компенсація механічного люфту редуктора при зміні напрямку
    const float compensated_angle = applyBacklashCompensation(state, cfg, state.current_angle_deg);

    // Розрахунок мікросекундного імпульсу ШІМ та передача на апаратний рівень
    state.last_pulse_us = angleToPulseUs(cfg, compensated_angle);
    if (pwm_cb_) {
        pwm_cb_(cfg.pin, state.last_pulse_us);
    }
}

float PanTiltDriver::smootherstep(float t) {
    // Обмеження аргументу діапазоном [0.0, 1.0]
    const float x = std::clamp(t, 0.0f, 1.0f);
    // Квінтичний поліном: 6x^5 - 15x^4 + 10x^3 забезпечує неперервність першої та другої похідних (плавне прискорення та гальмування)
    return x * x * x * (x * (x * 6.0f - 15.0f) + 10.0f);
}

float PanTiltDriver::applyBacklashCompensation(AxisState& state, const ServoConfig& cfg, float raw_angle) const {
    const float angle_diff = state.target_angle_deg - state.start_angle_deg;
    Direction current_dir = Direction::STOPPED;

    if (angle_diff > 0.01f) {
        current_dir = Direction::POSITIVE;
    } else if (angle_diff < -0.01f) {
        current_dir = Direction::NEGATIVE;
    }

    // Якщо напрямок змінився порівняно з попереднім рухом, редуктор обирає зазор між зубами
    float compensation_offset = 0.0f;
    if (current_dir != Direction::STOPPED) {
        if (state.last_direction != Direction::STOPPED && current_dir != state.last_direction) {
            // Додатковий кутовий зсув вала на величину люфту
            compensation_offset = (current_dir == Direction::POSITIVE) ? (cfg.backlash_deg * 0.5f) : (-cfg.backlash_deg * 0.5f);
        }
        state.last_direction = current_dir;
    }

    // Застосування поправки з обов'язковим урахуванням апаратних меж 0–180 градусів
    return std::clamp(raw_angle + compensation_offset, 0.0f, 180.0f);
}

uint32_t PanTiltDriver::angleToPulseUs(const ServoConfig& cfg, float angle_deg) const {
    // Лінійна інтерполяція: 0° -> min_pulse_us, 180° -> max_pulse_us
    const float clamped_angle = std::clamp(angle_deg, 0.0f, 180.0f);
    const float pulse = static_cast<float>(cfg.min_pulse_us) + 
                        (clamped_angle / 180.0f) * static_cast<float>(cfg.max_pulse_us - cfg.min_pulse_us);
    return static_cast<uint32_t>(std::round(pulse));
}

bool PanTiltDriver::isMoving(AxisId axis) const {
    return states_[static_cast<size_t>(axis)].in_motion;
}

bool PanTiltDriver::isMoving() const {
    return states_[0].in_motion || states_[1].in_motion;
}

float PanTiltDriver::getCurrentAngle(AxisId axis) const {
    return states_[static_cast<size_t>(axis)].current_angle_deg;
}

uint32_t PanTiltDriver::getCurrentPulseUs(AxisId axis) const {
    return states_[static_cast<size_t>(axis)].last_pulse_us;
}

void PanTiltDriver::emergencyStop() {
    for (auto& state : states_) {
        state.target_angle_deg = state.current_angle_deg;
        state.duration_us = 0;
        state.in_motion = false;
    }
}

} // namespace actuators
