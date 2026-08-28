namespace Health {

class InterCoreSupervisor {
public:
    constexpr InterCoreSupervisor() noexcept = default;

    uint16_t generate_challenge() noexcept {
        current_challenge_ = static_cast<uint16_t>(current_challenge_ * 31421U + 6927U);
        return current_challenge_;
    }

    bool verify_response(uint16_t response) noexcept {
        const uint16_t expected = static_cast<uint16_t>(~current_challenge_ ^ 0x5A5AU);

        if (response == expected) {
            missed_heartbeats_ = 0;
            safety_relay_state_ = true;
            return true;
        }

        ++missed_heartbeats_;
        if (missed_heartbeats_ >= 3) {
            safety_relay_state_ = false;
        }
        return false;
    }

    [[nodiscard]] bool is_safety_relay_closed() const noexcept { return safety_relay_state_; }

private:
    uint16_t current_challenge_{0x1234};
    uint32_t missed_heartbeats_{0};
    bool     safety_relay_state_{true};
};

} // namespace Health
