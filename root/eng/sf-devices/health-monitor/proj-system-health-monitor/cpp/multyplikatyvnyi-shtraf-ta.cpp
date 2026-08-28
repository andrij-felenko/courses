namespace Health {

template <size_t MaxComponents, size_t BlackboxSlots>
uint32_t Supervisor<MaxComponents, BlackboxSlots>::calculate_crc32(
    const uint8_t *data, size_t length) const noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t b = 0; b < 8; ++b) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(uint32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

template <size_t MaxComponents, size_t BlackboxSlots>
void Supervisor<MaxComponents, BlackboxSlots>::tick(uint64_t timestamp_ms) noexcept {
    ++iteration_counter_;
    if (warmup_ticks_left_ > 0) {
        --warmup_ticks_left_;
    }

    uint32_t weighted_score_sum = 0;
    uint32_t total_weight = 0;
    bool critical_fail = false;
    uint8_t failed_component_id = 0xFF;

    for (size_t i = 0; i < component_count_; ++i) {
        auto& comp = components_[i];
        uint16_t raw = comp.collector ? comp.collector() : 0;
        if (raw > ScorePerfect) {
            raw = ScorePerfect;
        }

        // EWMA згладжування з округленням: H[k] = (raw + 7 * H[k-1] + 4) >> 3
        comp.smoothed_score = static_cast<uint16_t>(
            (raw + static_cast<uint32_t>(comp.smoothed_score) * 7U + 4U) >> 3U
        );

        if (comp.smoothed_score < CriticalThreshold) {
            ++comp.consecutive_failures;
            if (comp.is_critical && warmup_ticks_left_ == 0) {
                critical_fail = true;
                failed_component_id = static_cast<uint8_t>(i);
            }
        } else {
            comp.consecutive_failures = 0;
        }

        weighted_score_sum += static_cast<uint32_t>(comp.smoothed_score) * comp.weight;
        total_weight += comp.weight;
    }

    system_score_ = (total_weight > 0) 
        ? static_cast<uint16_t>(weighted_score_sum / total_weight) 
        : 0;

    if (critical_fail) {
        system_score_ = 0;
        current_state_ = State::Emergency;
        log_emergency(failed_component_id, 0, 0, timestamp_ms);
    } else if (system_score_ >= NominalThreshold) {
        current_state_ = State::Nominal;
    } else if (system_score_ >= DegradedThreshold) {
        current_state_ = State::Degraded;
    } else if (system_score_ >= CriticalThreshold) {
        current_state_ = State::Critical;
    } else {
        current_state_ = State::Emergency;
        log_emergency(0xFE, 0, 0, timestamp_ms);
    }
}

template <size_t MaxComponents, size_t BlackboxSlots>
void Supervisor<MaxComponents, BlackboxSlots>::log_emergency(
    uint8_t faulty_id, uint32_t cfsr, uint32_t hfsr, uint64_t timestamp_ms) noexcept {
    auto& entry = blackbox_ring_[blackbox_head_];
    entry.magic = BlackboxMagic;
    entry.seq_num = ++blackbox_seq_;
    entry.timestamp_ms = timestamp_ms;
    entry.system_score = system_score_;
    entry.system_state = current_state_;
    entry.fault_component_id = faulty_id;
    entry.cfsr_reg = cfsr;
    entry.hfsr_reg = hfsr;
    entry.vdd_mv = 3300;
    entry.core_temp_c = 25;
    entry.min_stack_free_bytes = 128;

    entry.crc32 = calculate_crc32(reinterpret_cast<const uint8_t*>(&entry),
                                  sizeof(BlackboxEntry) - sizeof(uint32_t));

    blackbox_head_ = (blackbox_head_ + 1) % BlackboxSlots;
}

} // namespace Health
