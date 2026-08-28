class EscalationManager {
public:
    EscalationManager() = default;

    void update_trail(float x, float y, float z, float yaw, int8_t rssi, std::chrono::milliseconds now) noexcept {
        if (now - last_breadcrumb_time_ >= 1000ms) {
            last_breadcrumb_time_ = now;
            trail_.push({x, y, z, yaw, now, rssi});
        }
    }

    void tick(EscalationTrigger current_trigger,
              float dist_to_obstacle_m,
              float speed_mps,
              bool radio_link_alive,
              std::chrono::milliseconds now) noexcept
    {
        switch (state_) {
            case EscalationState::Autonomous:
                if (current_trigger != EscalationTrigger::None) {
                    active_trigger_ = current_trigger;
                    current_query_id_++;
                    request_started_ = now;
                    dynamic_deadline_ = calculate_dynamic_deadline(
                        dist_to_obstacle_m, speed_mps, 2.0f, 4.0f, 200ms);
                    
                    state_ = (dynamic_deadline_ == 0ms)
                             ? EscalationState::FailsafeHold
                             : EscalationState::EscalationRequested;
                }
                break;

            case EscalationState::EscalationRequested:
                state_ = EscalationState::AwaitingOperator;
                break;

            case EscalationState::AwaitingOperator: {
                const auto elapsed = now - request_started_;
                if (!radio_link_alive || elapsed >= dynamic_deadline_) {
                    state_ = EscalationState::FailsafeHold;
                }
                break;
            }

            case EscalationState::ApplyingOverride:
                state_ = EscalationState::Autonomous;
                active_trigger_ = EscalationTrigger::None;
                break;

            case EscalationState::FailsafeHold:
                if (now - request_started_ > (dynamic_deadline_ + 5000ms)) {
                    state_ = EscalationState::FailsafeBacktrack;
                }
                break;

            case EscalationState::FailsafeBacktrack:
                if (trail_.size() == 0) {
                    state_ = EscalationState::FailsafeSafeAbort;
                }
                break;

            case EscalationState::FailsafeSafeAbort:
                break;
        }
    }

    [[nodiscard]] bool handle_response(uint16_t query_id, uint8_t option_id, std::chrono::milliseconds now) noexcept {
        if (state_ != EscalationState::AwaitingOperator) {
            return false;
        }
        if (query_id != current_query_id_) {
            return false;
        }
        if (now - request_started_ > dynamic_deadline_) {
            return false;
        }

        selected_option_id_ = option_id;
        state_ = EscalationState::ApplyingOverride;
        return true;
    }

    [[nodiscard]] EscalationState state() const noexcept { return state_; }
    [[nodiscard]] uint16_t query_id() const noexcept { return current_query_id_; }
    [[nodiscard]] std::chrono::milliseconds deadline() const noexcept { return dynamic_deadline_; }

private:
    EscalationState state_{EscalationState::Autonomous};
    EscalationTrigger active_trigger_{EscalationTrigger::None};
    uint16_t current_query_id_{0};
    std::chrono::milliseconds request_started_{0ms};
    std::chrono::milliseconds dynamic_deadline_{0ms};
    uint8_t selected_option_id_{0};
    BreadcrumbTrail trail_{};
    std::chrono::milliseconds last_breadcrumb_time_{0ms};
};
