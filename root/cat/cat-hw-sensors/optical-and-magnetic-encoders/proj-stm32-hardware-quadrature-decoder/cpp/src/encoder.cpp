#include "encoder.hpp"
#include <cmath>

namespace {
    constexpr float PI_F = 3.14159265358979323846f;
    constexpr float TWO_PI_F = 2.0f * PI_F;
    constexpr float RAD_TO_DEG = 180.0f / PI_F;
    constexpr float SEC_TO_MIN = 60.0f;
}

QuadratureEncoder::QuadratureEncoder(ITimerPeripheral& timer, const EncoderConfig& config)
    : timer_(timer)
    , config_(config) {
    uint32_t multiplier = config_.x4_encoding ? 4U : 2U;
    counts_per_rev_ = config_.pulses_per_revolution * multiplier;
    if (counts_per_rev_ == 0) {
        counts_per_rev_ = 1; // Запобігання діленню на нуль
    }
}

void QuadratureEncoder::init() {
    overflow_count_ = 0;
    last_sampled_position_ = 0;
    state_ = EncoderState{};

    // Конфігурація апаратного таймера та периферії
    timer_.initEncoderMode(config_.filter_icf);
    timer_.enableUpdateInterrupt();
    timer_.configureExtiZPin();
}

void QuadratureEncoder::handleTimerOverflowISR() {
    // При лічбі вгору (CNT: 65535 -> 0) додаємо +1 до старших бітів
    // При лічбі вниз (CNT: 0 -> 65535) віднімаємо -1 від старших бітів
    if (timer_.isCountingDown()) {
        overflow_count_--;
    } else {
        overflow_count_++;
    }
}

void QuadratureEncoder::handleIndexPulseISR() {
    // Зчитуємо поточну апаратну позицію на момент надходження Z-мітки
    int32_t current_raw = calculateContinuousPosition();
    
    // Встановлюємо калібрувальний зсув для відносної точки відліку
    state_.zero_offset_counts = current_raw;
    state_.is_calibrated = true;
}

int32_t QuadratureEncoder::calculateContinuousPosition() const {
    // Алгоритм подвійної перевірки (double-check pattern) для усунення перегонів (race conditions)
    // між зчитаним значенням overflow_count_ та апаратним лічильником CNT
    int32_t overflows = overflow_count_;
    uint16_t cnt = timer_.getCounter();
    int32_t overflows_check = overflow_count_;

    if (overflows != overflows_check) {
        // Якщо під час зчитання CNT відбулося ISR переповнення, перечитуємо актуальне значення
        overflows = overflows_check;
        cnt = timer_.getCounter();
    }

    int32_t continuous_pos = (overflows << 16) | static_cast<int32_t>(cnt);

    if (config_.invert_direction) {
        continuous_pos = -continuous_pos;
    }

    return continuous_pos;
}

void QuadratureEncoder::update(float dt_seconds) {
    if (dt_seconds <= 0.0f) {
        return;
    }

    // 1. Оновлення суцільної 32-бітної позиції
    int32_t current_pos = calculateContinuousPosition();
    state_.raw_position_counts = current_pos;

    // 2. Обчислення відносної позиції з урахуванням Z-мітки
    int32_t position_relative = current_pos - state_.zero_offset_counts;

    // 3. Перерахунок позиції в кутові величини
    float revolutions = static_cast<float>(position_relative) / static_cast<float>(counts_per_rev_);
    state_.angle_radians = revolutions * TWO_PI_F;
    state_.angle_degrees = state_.angle_radians * RAD_TO_DEG;

    // 4. Чисельне диференціювання для розрахунку кутової швидкості
    // delta_counts = N(t) - N(t - dt)
    int32_t delta_counts = current_pos - last_sampled_position_;
    last_sampled_position_ = current_pos;

    float delta_revolutions = static_cast<float>(delta_counts) / static_cast<float>(counts_per_rev_);
    
    // w = (2 * pi * delta_N) / (CPR * dt) [рад/с]
    state_.velocity_rad_per_sec = (delta_revolutions * TWO_PI_F) / dt_seconds;
    
    // RPM = (delta_N * 60) / (CPR * dt) [об/хв]
    state_.velocity_rpm = (delta_revolutions * SEC_TO_MIN) / dt_seconds;
}

int32_t QuadratureEncoder::getPosition() const {
    return state_.raw_position_counts;
}

float QuadratureEncoder::getAngleRad() const {
    return state_.angle_radians;
}

float QuadratureEncoder::getAngleDeg() const {
    return state_.angle_degrees;
}

float QuadratureEncoder::getVelocityRadSec() const {
    return state_.velocity_rad_per_sec;
}

float QuadratureEncoder::getVelocityRPM() const {
    return state_.velocity_rpm;
}

EncoderState QuadratureEncoder::getState() const {
    return state_;
}

bool QuadratureEncoder::isCalibrated() const {
    return state_.is_calibrated;
}

void QuadratureEncoder::resetPosition(int32_t new_position) {
    // Безпечне програмне встановлення лічильника
    timer_.disableUpdateInterrupt();
    
    overflow_count_ = new_position >> 16;
    timer_.setCounter(static_cast<uint16_t>(new_position & 0xFFFF));
    last_sampled_position_ = new_position;
    state_.raw_position_counts = new_position;
    state_.zero_offset_counts = new_position;
    
    timer_.enableUpdateInterrupt();
}

uint32_t QuadratureEncoder::getCountsPerRev() const {
    return counts_per_rev_;
}
