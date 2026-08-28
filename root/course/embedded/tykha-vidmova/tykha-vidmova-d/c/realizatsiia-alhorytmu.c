void sensor_guard_init(sensor_guard_t *g, const sensor_guard_cfg_t *cfg) {
    if (!g || !cfg) return;
    g->cfg = *cfg;
    g->prev_val = 0.0f;
    g->prev_ts_ms = 0;
    g->has_history = false;
    g->count = 0;
    g->mean = 0.0f;
    g->m2 = 0.0f;
    g->status_flags = SENSOR_OK;
}

uint8_t sensor_guard_process(sensor_guard_t *g, float sample, uint32_t now_ms) {
    if (!g) return SENSOR_ERR_RANGE_LOW;

    uint8_t flags = SENSOR_OK;

    /* 1. Перевірка фізичних меж */
    if (sample < g->cfg.min_valid) {
        flags |= SENSOR_ERR_RANGE_LOW;
    } else if (sample > g->cfg.max_valid) {
        flags |= SENSOR_ERR_RANGE_HIGH;
    }

    /* 2. Градієнтний контроль (швидкість наростання) */
    if (g->has_history) {
        uint32_t dt_ms = now_ms - g->prev_ts_ms;
        if (dt_ms > 0) {
            float dt_s = (float)dt_ms / 1000.0f;
            float gradient = fabsf(sample - g->prev_val) / dt_s;
            if (gradient > g->cfg.max_gradient_per_s) {
                flags |= SENSOR_ERR_SLEW_RATE;
            }
        }
    }

    /* 3. Ітеративний розрахунок дисперсії Уелфорда */
    g->count++;
    float d1 = sample - g->mean;
    g->mean += d1 / (float)g->count;
    float d2 = sample - g->mean;
    g->m2 += d1 * d2;

    /* Перевірка нульової дисперсії після накопичення базового вікна */
    if (g->count >= g->cfg.variance_window) {
        float var = g->m2 / (float)(g->count - 1);
        if (var < g->cfg.min_noise_variance) {
            flags |= SENSOR_ERR_ZERO_VARIANCE;
        }
    }

    g->prev_val = sample;
    g->prev_ts_ms = now_ms;
    g->has_history = true;
    g->status_flags = flags;

    return flags;
}
