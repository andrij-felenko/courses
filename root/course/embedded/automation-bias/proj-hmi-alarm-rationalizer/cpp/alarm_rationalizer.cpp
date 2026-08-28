#include "alarm_rationalizer.hpp"
#include <algorithm>
#include <cmath>

namespace isa18_2 {

AlarmRationalizer::AlarmRationalizer() noexcept {
    rate_history_.fill(0ms);
}

bool AlarmRationalizer::register_alarm(const AlarmConfig& cfg) noexcept {
    if (count_ >= MaxAlarms) {
        return false;
    }
    configs_[count_] = cfg;
    runtimes_[count_] = AlarmRuntime{};
    count_++;
    return true;
}

void AlarmRationalizer::set_system_state(SystemStateMask state, std::chrono::milliseconds /*now*/) noexcept {
    current_sys_state_ = state;
}

void AlarmRationalizer::update_value(uint16_t alarm_id, float value, std::chrono::milliseconds /*now*/) noexcept {
    if (alarm_id < count_) {
        runtimes_[alarm_id].current_value = value;
    }
}

void AlarmRationalizer::evaluate_raw_trip(const AlarmConfig& cfg, AlarmRuntime& rt) noexcept {
    if (cfg.is_high_alarm) {
        if (rt.raw_trip_condition) {
            if (rt.current_value <= cfg.clear_threshold) {
                rt.raw_trip_condition = false;
            }
        } else {
            if (rt.current_value >= cfg.trip_threshold) {
                rt.raw_trip_condition = true;
            }
        }
    } else {
        if (rt.raw_trip_condition) {
            if (rt.current_value >= cfg.clear_threshold) {
                rt.raw_trip_condition = false;
            }
        } else {
            if (rt.current_value <= cfg.trip_threshold) {
                rt.raw_trip_condition = true;
            }
        }
    }
}

void AlarmRationalizer::update_chatter(const AlarmConfig& cfg, AlarmRuntime& rt, std::chrono::milliseconds now) noexcept {
    if (cfg.chatter_limit == 0 || cfg.chatter_window == 0ms) {
        rt.is_chattering = false;
        return;
    }

    if (rt.first_transition_in_window == 0ms || (now - rt.first_transition_in_window) > cfg.chatter_window) {
        rt.first_transition_in_window = now;
        rt.transitions_in_window = 1;
        rt.is_chattering = false;
    } else {
        rt.transitions_in_window++;
        if (rt.transitions_in_window >= cfg.chatter_limit) {
            rt.is_chattering = true;
        }
    }
}

void AlarmRationalizer::add_rate_event(std::chrono::milliseconds now) noexcept {
    const size_t capacity = rate_history_.size();
    rate_history_[rate_head_] = now;
    rate_head_ = (rate_head_ + 1) % capacity;
    if (rate_head_ == rate_tail_) {
        rate_tail_ = (rate_tail_ + 1) % capacity;
    }
}

void AlarmRationalizer::update_rate_metrics(std::chrono::milliseconds now) noexcept {
    const size_t capacity = rate_history_.size();
    const auto cutoff = (now >= AlarmRateWindow) ? (now - AlarmRateWindow) : 0ms;

    while (rate_tail_ != rate_head_) {
        if (rate_history_[rate_tail_] < cutoff) {
            rate_tail_ = (rate_tail_ + 1) % capacity;
        } else {
            break;
        }
    }

    if (rate_head_ >= rate_tail_) {
        alarms_in_window_ = rate_head_ - rate_tail_;
    } else {
        alarms_in_window_ = capacity - (rate_tail_ - rate_head_);
    }

    is_alarm_flood_ = (alarms_in_window_ >= AlarmFloodThreshold);
}

void AlarmRationalizer::process(std::chrono::milliseconds now) noexcept {
    // Фаза 1: Оцінка пригнічення за станом та батьківськими подіями
    for (size_t i = 0; i < count_; ++i) {
        const auto& cfg = configs_[i];
        auto& rt = runtimes_[i];

        rt.is_suppressed_by_state = (current_sys_state_ & cfg.suppression_mask);

        rt.is_suppressed_by_parent = false;
        if (cfg.parent_alarm_id.has_value()) {
            const auto parent_id = *cfg.parent_alarm_id;
            if (parent_id < count_) {
                const auto parent_state = runtimes_[parent_id].state;
                if (parent_state == AlarmState::UnacknowledgedAlarm || parent_state == AlarmState::AcknowledgedAlarm) {
                    rt.is_suppressed_by_parent = true;
                }
            }
        }

        // Перевірка таймуату тимчасово відкладених тривог
        if (rt.state == AlarmState::Shelved && now >= rt.shelved_until_time) {
            rt.state = rt.raw_trip_condition ? AlarmState::UnacknowledgedAlarm : AlarmState::Normal;
            rt.state_change_time = now;
        }
    }

    // Фаза 2: Обчислення автомата станів ISA-18.2
    for (size_t i = 0; i < count_; ++i) {
        const auto& cfg = configs_[i];
        auto& rt = runtimes_[i];

        if (rt.state == AlarmState::OutOfService) {
            continue;
        }

        const bool should_suppress = rt.is_suppressed_by_state || rt.is_suppressed_by_parent;
        if (should_suppress) {
            if (rt.state != AlarmState::SuppressedByDesign && rt.state != AlarmState::Shelved) {
                rt.prev_state = rt.state;
                rt.state = AlarmState::SuppressedByDesign;
                rt.state_change_time = now;
                total_suppressions_++;
            }
            continue;
        } else {
            if (rt.state == AlarmState::SuppressedByDesign) {
                rt.state = AlarmState::Normal;
                rt.state_change_time = now;
            }
        }

        if (rt.state == AlarmState::Shelved) {
            continue;
        }

        const bool old_raw = rt.raw_trip_condition;
        evaluate_raw_trip(cfg, rt);

        if (old_raw != rt.raw_trip_condition) {
            update_chatter(cfg, rt, now);
            if (rt.is_chattering) {
                total_chatter_events_++;
            }
        }

        // Затримки On-Delay / Off-Delay
        bool active_filtered = false;
        if (rt.raw_trip_condition) {
            rt.clear_start_time = 0ms;
            if (rt.trip_start_time == 0ms) {
                rt.trip_start_time = now;
            }
            if ((now - rt.trip_start_time) >= cfg.on_delay) {
                active_filtered = true;
            }
        } else {
            rt.trip_start_time = 0ms;
            if (rt.clear_start_time == 0ms) {
                rt.clear_start_time = now;
            }
            if ((now - rt.clear_start_time) < cfg.off_delay) {
                active_filtered = true;
            }
        }

        auto next_state = rt.state;
        switch (rt.state) {
            case AlarmState::Normal:
                if (active_filtered && !rt.is_chattering) {
                    next_state = AlarmState::UnacknowledgedAlarm;
                    total_trips_++;
                    add_rate_event(now);
                }
                break;

            case AlarmState::UnacknowledgedAlarm:
                if (!active_filtered) {
                    next_state = AlarmState::ReturnToNormalUnack;
                }
                break;

            case AlarmState::AcknowledgedAlarm:
                if (!active_filtered) {
                    next_state = AlarmState::Normal;
                }
                break;

            case AlarmState::ReturnToNormalUnack:
                if (active_filtered) {
                    next_state = AlarmState::UnacknowledgedAlarm;
                }
                break;

            default:
                break;
        }

        if (next_state != rt.state) {
            rt.prev_state = rt.state;
            rt.state = next_state;
            rt.state_change_time = now;
        }
    }

    update_rate_metrics(now);
}

bool AlarmRationalizer::acknowledge(uint16_t alarm_id, std::chrono::milliseconds now) noexcept {
    if (alarm_id >= count_) return false;
    auto& rt = runtimes_[alarm_id];

    if (rt.state == AlarmState::UnacknowledgedAlarm) {
        rt.prev_state = rt.state;
        rt.state = AlarmState::AcknowledgedAlarm;
        rt.state_change_time = now;
        total_acks_++;
        return true;
    } else if (rt.state == AlarmState::ReturnToNormalUnack) {
        rt.prev_state = rt.state;
        rt.state = AlarmState::Normal;
        rt.state_change_time = now;
        total_acks_++;
        return true;
    }
    return false;
}

bool AlarmRationalizer::shelve(uint16_t alarm_id, std::chrono::milliseconds duration, std::chrono::milliseconds now) noexcept {
    if (alarm_id >= count_ || duration == 0ms) return false;
    auto& rt = runtimes_[alarm_id];

    if (rt.state == AlarmState::UnacknowledgedAlarm || rt.state == AlarmState::AcknowledgedAlarm) {
        rt.prev_state = rt.state;
        rt.state = AlarmState::Shelved;
        rt.shelved_until_time = now + duration;
        rt.state_change_time = now;
        return true;
    }
    return false;
}

bool AlarmRationalizer::unshelve(uint16_t alarm_id, std::chrono::milliseconds now) noexcept {
    if (alarm_id >= count_) return false;
    auto& rt = runtimes_[alarm_id];

    if (rt.state == AlarmState::Shelved) {
        rt.prev_state = rt.state;
        rt.state = rt.raw_trip_condition ? AlarmState::UnacknowledgedAlarm : AlarmState::Normal;
        rt.shelved_until_time = 0ms;
        rt.state_change_time = now;
        return true;
    }
    return false;
}

std::vector<uint16_t> AlarmRationalizer::get_active_hmi_alarms() const {
    std::vector<uint16_t> active_ids;
    active_ids.reserve(count_);

    for (size_t i = 0; i < count_; ++i) {
        const auto s = runtimes_[i].state;
        if (s == AlarmState::UnacknowledgedAlarm || s == AlarmState::AcknowledgedAlarm || s == AlarmState::ReturnToNormalUnack) {
            active_ids.push_back(static_cast<uint16_t>(i));
        }
    }

    std::sort(active_ids.begin(), active_ids.end(), [this](uint16_t a, uint16_t b) {
        return static_cast<uint8_t>(configs_[a].priority) > static_cast<uint8_t>(configs_[b].priority);
    });

    return active_ids;
}

const AlarmConfig& AlarmRationalizer::get_config(uint16_t alarm_id) const {
    return configs_.at(alarm_id);
}

const AlarmRuntime& AlarmRationalizer::get_runtime(uint16_t alarm_id) const {
    return runtimes_.at(alarm_id);
}

} // namespace isa18_2
