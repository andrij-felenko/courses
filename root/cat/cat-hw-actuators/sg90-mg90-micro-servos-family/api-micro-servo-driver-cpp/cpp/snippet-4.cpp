void MicroServo::setAngle(float angle_deg) {
    if (!is_attached_) return;
    float clamped = std::clamp(angle_deg, cfg_.soft_limit_min_deg, cfg_.soft_limit_max_deg);
    float span_deg = cfg_.max_angle_deg - cfg_.min_angle_deg;
    float span_us = static_cast<float>(cfg_.max_pulse_us - cfg_.min_pulse_us);

    float pulse = static_cast<float>(cfg_.min_pulse_us) +
                  (clamped - cfg_.min_angle_deg) * span_us / span_deg;
    current_angle_ = clamped;
    set_pwm_us_(static_cast<uint16_t>(pulse + 0.5f));
}

void MicroServo::setPulseUs(uint16_t pulse_us) {
    if (!is_attached_) return;
    uint16_t safe_us = std::clamp(pulse_us, cfg_.min_pulse_us, cfg_.max_pulse_us);
    set_pwm_us_(safe_us);
}
