static uint32_t health_calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t b = 0; b < 8; ++b) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(uint32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

void health_supervisor_init(health_supervisor_t *ctx) {
    if (!ctx) return;
    ctx->component_count = 0;
    ctx->system_score = HEALTH_SCORE_PERFECT;
    ctx->current_state = HEALTH_STATE_NOMINAL;
    ctx->iteration_counter = 0;
    ctx->warmup_ticks_left = HEALTH_WARMUP_TICKS;
    ctx->blackbox_head = 0;
    ctx->blackbox_seq = 0;

    for (size_t i = 0; i < HEALTH_BLACKBOX_SLOTS; ++i) {
        ctx->blackbox_ring[i].magic = 0;
    }
}

bool health_supervisor_register(health_supervisor_t *ctx,
                                const char *name,
                                health_collector_fn collector,
                                void *user_ctx,
                                uint16_t weight,
                                bool is_critical) {
    if (!ctx || ctx->component_count >= HEALTH_MAX_COMPONENTS || !collector) {
        return false;
    }

    health_component_desc_t *c = &ctx->components[ctx->component_count++];
    c->name = name ? name : "Unnamed";
    c->collector = collector;
    c->user_ctx = user_ctx;
    c->weight = (weight > 0) ? weight : 1;
    c->is_critical = is_critical;
    c->smoothed_score = HEALTH_SCORE_PERFECT;
    c->consecutive_failures = 0;
    return true;
}

void health_supervisor_tick(health_supervisor_t *ctx, uint64_t timestamp_ms) {
    if (!ctx) return;

    ctx->iteration_counter++;
    if (ctx->warmup_ticks_left > 0) {
        ctx->warmup_ticks_left--;
    }

    uint32_t weighted_score_sum = 0;
    uint32_t total_weight = 0;
    bool critical_fail = false;
    uint8_t failed_component_id = 0xFF;

    for (uint8_t i = 0; i < ctx->component_count; ++i) {
        health_component_desc_t *c = &ctx->components[i];
        uint16_t raw = c->collector(c->user_ctx);

        if (raw > HEALTH_SCORE_PERFECT) {
            raw = HEALTH_SCORE_PERFECT;
        }

        // EWMA згладжування з округленням до найближчого: H[k] = (raw + 7 * H[k-1] + 4) / 8
        c->smoothed_score = (uint16_t)((raw + (uint32_t)c->smoothed_score * 7U + 4U) >> 3U);

        if (c->smoothed_score < HEALTH_CRITICAL_THRESHOLD) {
            c->consecutive_failures++;
            if (c->is_critical && ctx->warmup_ticks_left == 0) {
                critical_fail = true;
                failed_component_id = i;
            }
        } else {
            c->consecutive_failures = 0;
        }

        weighted_score_sum += (uint32_t)c->smoothed_score * c->weight;
        total_weight += c->weight;
    }

    if (total_weight > 0) {
        ctx->system_score = (uint16_t)(weighted_score_sum / total_weight);
    } else {
        ctx->system_score = 0;
    }

    // Мультиплікативний штраф для критичних підсистем
    if (critical_fail) {
        ctx->system_score = 0;
        ctx->current_state = HEALTH_STATE_EMERGENCY;
        health_supervisor_log_emergency(ctx, failed_component_id, 0, 0, timestamp_ms);
    } else if (ctx->system_score >= HEALTH_NOMINAL_THRESHOLD) {
        ctx->current_state = HEALTH_STATE_NOMINAL;
    } else if (ctx->system_score >= HEALTH_DEGRADED_THRESHOLD) {
        ctx->current_state = HEALTH_STATE_DEGRADED;
    } else if (ctx->system_score >= HEALTH_CRITICAL_THRESHOLD) {
        ctx->current_state = HEALTH_STATE_CRITICAL;
    } else {
        ctx->current_state = HEALTH_STATE_EMERGENCY;
        health_supervisor_log_emergency(ctx, 0xFE, 0, 0, timestamp_ms);
    }
}

void health_supervisor_log_emergency(health_supervisor_t *ctx, 
                                     uint8_t faulty_id, 
                                     uint32_t cfsr, 
                                     uint32_t hfsr,
                                     uint64_t timestamp_ms) {
    if (!ctx) return;

    health_blackbox_entry_t *entry = &ctx->blackbox_ring[ctx->blackbox_head];
    entry->magic = HEALTH_BLACKBOX_MAGIC;
    entry->seq_num = ++ctx->blackbox_seq;
    entry->timestamp_ms = timestamp_ms;
    entry->system_score = ctx->system_score;
    entry->system_state = (uint8_t)ctx->current_state;
    entry->fault_component_id = faulty_id;
    entry->cfsr_reg = cfsr;
    entry->hfsr_reg = hfsr;
    entry->vdd_mv = 3300;
    entry->core_temp_c = 25;
    entry->min_stack_free_bytes = 128;

    entry->crc32 = health_calculate_crc32((const uint8_t *)entry, 
                                          offsetof(health_blackbox_entry_t, crc32));

    ctx->blackbox_head = (ctx->blackbox_head + 1) % HEALTH_BLACKBOX_SLOTS;
}
