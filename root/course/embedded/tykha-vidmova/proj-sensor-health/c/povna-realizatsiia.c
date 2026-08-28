void sensor_guard_init(sensor_guard_t *guard, const sensor_guard_config_t *cfg) {
    if (!guard || !cfg) return;
    guard->cfg = *cfg;
    guard->last_value = 0.0f;
    guard->last_timestamp_ms = 0;
    guard->has_prev_sample = false;
    guard->sample_count = 0;
    guard->mean = 0.0f;
    guard->m2 = 0.0f;
    guard->flags = SENSOR_HEALTH_OK;
}

uint8_t sensor_guard_update(sensor_guard_t *guard, float value, uint32_t timestamp_ms) {
    if (!guard) return SENSOR_FAULT_OUT_OF_RANGE_LOW;

    uint8_t current_faults = SENSOR_HEALTH_OK;

    /* 1. Перевірка фізичних меж (Plausibility) */
    if (value < guard->cfg.min_plausible) {
        current_faults |= SENSOR_FAULT_OUT_OF_RANGE_LOW;
    } else if (value > guard->cfg.max_plausible) {
        current_faults |= SENSOR_FAULT_OUT_OF_RANGE_HIGH;
    }

    /* 2. Градієнтний контроль швидкості зміни (dY/dt) */
    if (guard->has_prev_sample) {
        uint32_t dt_ms = timestamp_ms - guard->last_timestamp_ms;
        if (dt_ms > 0) {
            float dt_sec = (float)dt_ms / 1000.0f;
            float rate = fabsf(value - guard->last_value) / dt_sec;
            if (rate > guard->cfg.max_slew_rate) {
                current_faults |= SENSOR_FAULT_SLEW_RATE;
            }
        }
    }

    /* 3. Однопрохідний розрахунок дисперсії (Алгоритм Уелфорда) */
    guard->sample_count++;
    float delta = value - guard->mean;
    guard->mean += delta / (float)guard->sample_count;
    float delta2 = value - guard->mean;
    guard->m2 += delta * delta2;

    /* Перевірка застрягання значення (Zero-Variance) після накопичення мінімального вікна */
    if (guard->sample_count >= guard->cfg.min_samples_var) {
        float variance = guard->m2 / (float)(guard->sample_count - 1);
        if (variance < guard->cfg.min_variance) {
            current_faults |= SENSOR_FAULT_ZERO_VARIANCE;
        }
    }

    guard->last_value = value;
    guard->last_timestamp_ms = timestamp_ms;
    guard->has_prev_sample = true;
    guard->flags = current_faults;

    return current_faults;
}

quorum_result_t sensor_guard_vote_2oo3(float s1, float s2, float s3, float max_allowed_spread) {
    quorum_result_t res;
    res.voted_value = 0.0f;
    res.quorum_valid = false;
    res.faulty_sensor_mask = 0;

    float diff12 = fabsf(s1 - s2);
    float diff23 = fabsf(s2 - s3);
    float diff31 = fabsf(s3 - s1);

    bool p12 = (diff12 <= max_allowed_spread);
    bool p23 = (diff23 <= max_allowed_spread);
    bool p31 = (diff31 <= max_allowed_spread);

    if (p12 && p23 && p31) {
        /* Усі три канали узгоджені: повертаємо середнє або медіану */
        res.voted_value = (s1 + s2 + s3) / 3.0f;
        res.quorum_valid = true;
    } else if (p12) {
        /* Канал 3 відхилився */
        res.voted_value = (s1 + s2) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 2);
    } else if (p23) {
        /* Канал 1 відхилився */
        res.voted_value = (s2 + s3) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 0);
    } else if (p31) {
        /* Канал 2 відхилився */
        res.voted_value = (s3 + s1) / 2.0f;
        res.quorum_valid = true;
        res.faulty_sensor_mask = (1 << 1);
    } else {
        /* Усі три канали розійшлися: кворум втрачено */
        res.quorum_valid = false;
        res.faulty_sensor_mask = 0x07;
    }

    return res;
}
