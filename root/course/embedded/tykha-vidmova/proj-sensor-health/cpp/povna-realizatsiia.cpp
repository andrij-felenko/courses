SensorHealthFlags SensorHealthGuard::update(float value, uint32_t timestamp_ms) noexcept {
    auto current_faults = SensorHealthFlags::Ok;

    // 1. Перевірка фізичних меж
    if (value < cfg_.min_plausible) {
        current_faults = current_faults | SensorHealthFlags::OutOfRangeLow;
    } else if (value > cfg_.max_plausible) {
        current_faults = current_faults | SensorHealthFlags::OutOfRangeHigh;
    }

    // 2. Градієнтний контроль (dY/dt)
    if (has_prev_sample_) {
        const uint32_t dt_ms = timestamp_ms - last_timestamp_ms_;
        if (dt_ms > 0) {
            const float dt_s = static_cast<float>(dt_ms) / 1000.0f;
            const float rate = std::abs(value - last_value_) / dt_s;
            if (rate > cfg_.max_slew_rate) {
                current_faults = current_faults | SensorHealthFlags::SlewRate;
            }
        }
    }

    // 3. Алгоритм Уелфорда для дисперсії
    sample_count_++;
    const float delta = value - mean_;
    mean_ += delta / static_cast<float>(sample_count_);
    const float delta2 = value - mean_;
    m2_ += delta * delta2;

    if (sample_count_ >= cfg_.min_samples_var) {
        const float var = m2_ / static_cast<float>(sample_count_ - 1);
        if (var < cfg_.min_noise_variance) {
            current_faults = current_faults | SensorHealthFlags::ZeroVariance;
        }
    }

    last_value_ = value;
    last_timestamp_ms_ = timestamp_ms;
    has_prev_sample_ = true;
    flags_ = current_faults;

    return flags_;
}

float SensorHealthGuard::variance() const noexcept {
    if (sample_count_ < 2) {
        return 0.0f;
    }
    return m2_ / static_cast<float>(sample_count_ - 1);
}

QuorumResult SensorHealthGuard::vote_2oo3(float s1, float s2, float s3, float max_allowed_spread) noexcept {
    QuorumResult res{};

    const float diff12 = std::abs(s1 - s2);
    const float diff23 = std::abs(s2 - s3);
    const float diff31 = std::abs(s3 - s1);

    const bool p12 = (diff12 <= max_allowed_spread);
    const bool p23 = (diff23 <= max_allowed_spread);
    const bool p31 = (diff31 <= max_allowed_spread);

    if (p12 && p23 && p31) {
        res.voted_value = (s1 + s2 + s3) / 3.0f;
        res.quorum_valid = true;
    } else if (p12) {
        res.voted_value = (s1 + s2) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 2);
    } else if (p23) {
        res.voted_value = (s2 + s3) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 0);
    } else if (p31) {
        res.voted_value = (s3 + s1) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 1);
    } else {
        res.quorum_valid = false;
        res.faulty_sensor_mask = 0x07;
    }

    return res;
}
