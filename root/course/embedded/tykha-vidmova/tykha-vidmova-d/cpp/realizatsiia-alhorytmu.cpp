SensorError SensorGuard::process(float sample, uint32_t now_ms) noexcept {
    auto flags = SensorError::Ok;

    // 1. Фізичні межі
    if (sample < cfg_.min_valid) {
        flags = flags | SensorError::RangeLow;
    } else if (sample > cfg_.max_valid) {
        flags = flags | SensorError::RangeHigh;
    }

    // 2. Градієнтний контроль (dY/dt)
    if (has_history_) {
        const uint32_t dt_ms = now_ms - prev_ts_ms_;
        if (dt_ms > 0) {
            const float dt_s = static_cast<float>(dt_ms) / 1000.0f;
            const float gradient = std::abs(sample - prev_val_) / dt_s;
            if (gradient > cfg_.max_gradient_per_s) {
                flags = flags | SensorError::SlewRate;
            }
        }
    }

    // 3. Алгоритм Уелфорда
    count_++;
    const float d1 = sample - mean_;
    mean_ += d1 / static_cast<float>(count_);
    const float d2 = sample - mean_;
    m2_ += d1 * d2;

    if (count_ >= cfg_.variance_window) {
        const float var = m2_ / static_cast<float>(count_ - 1);
        if (var < cfg_.min_noise_variance) {
            flags = flags | SensorError::ZeroVariance;
        }
    }

    prev_val_ = sample;
    prev_ts_ms_ = now_ms;
    has_history_ = true;
    status_ = flags;

    return status_;
}

float SensorGuard::variance() const noexcept {
    if (count_ < 2) {
        return 0.0f;
    }
    return m2_ / static_cast<float>(count_ - 1);
}
