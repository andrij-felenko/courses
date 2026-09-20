EnablingState process(uint16_t tick_ms) noexcept {
    const bool raw_a = config_.read_ch_a();
    const bool raw_b = config_.read_ch_b();

    if (raw_a == raw_b) {
        discrepancy_timer_ = 0;
        if (!raw_a) {
            if (current_state_ == EnablingState::Enabled) {
                current_state_ = EnablingState::Panic;
            } else if (current_state_ != EnablingState::Panic) {
                current_state_ = EnablingState::Released;
            }
        } else {
            if (current_state_ == EnablingState::Released || current_state_ == EnablingState::Enabled) {
                current_state_ = EnablingState::Enabled;
            }
        }
    } else {
        discrepancy_timer_ += tick_ms;
        if (discrepancy_timer_ >= config_.discrepancy_ms) {
            current_state_ = EnablingState::Fault;
        }
    }

    return current_state_;
}
