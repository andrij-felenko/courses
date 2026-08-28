#pragma once

#include <cstdint>
#include <optional>
#include <expected>
#include <span>

namespace auth::arbiter {

inline constexpr uint32_t HeartbeatTimeoutMs = 1000;
inline constexpr uint32_t HandoverTimeoutMs  = 5000;
inline constexpr int16_t  DeadbandLimit      = 30; // 3% від 1000

enum class RoleFlags : uint8_t {
    None      = 0x00,
    Monitor   = 0x01,
    Pilot     = 0x02,
    Payload   = 0x04,
    Commander = 0x08
};

[[nodiscard]] constexpr RoleFlags operator|(RoleFlags a, RoleFlags b) noexcept {
    return static_cast<RoleFlags>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

enum class State : uint8_t {
    Idle,
    PilotActive,
    HandoverWaitStick,
    LinkLost,
    CommanderLocked
};

enum class ArbiterError : uint8_t {
    Unauthorized,
    AlreadyLocked,
    StickNotNeutral,
    Timeout,
    StateMismatch
};

struct StickAxes {
    int16_t roll{0};      // -1000 .. +1000
    int16_t pitch{0};     // -1000 .. +1000
    int16_t yaw{0};       // -1000 .. +1000
    int16_t throttle{0};  // 0 .. 1000

    [[nodiscard]] constexpr bool is_neutral(int16_t limit = DeadbandLimit) const noexcept {
        return (roll >= -limit && roll <= limit) &&
               (pitch >= -limit && pitch <= limit) &&
               (yaw >= -limit && yaw <= limit);
    }
};

class StationArbiter {
public:
    constexpr StationArbiter() noexcept {
        reset();
    }

    void reset() noexcept {
        pilot_gcs_id_ = 0;
        payload_gcs_id_ = 0;
        pending_pilot_gcs_id_ = 0;
        pilot_lease_deadline_ = 0;
        handover_deadline_ = 0;
        token_nonce_ = next_nonce();
        state_ = State::Idle;
    }

    [[nodiscard]] std::expected<uint32_t, ArbiterError> request_pilot_token(uint8_t gcs_id, uint32_t now_ms) noexcept {
        if (state_ == State::CommanderLocked) {
            return std::unexpected(ArbiterError::AlreadyLocked);
        }
        if (state_ == State::Idle || state_ == State::LinkLost) {
            pilot_gcs_id_ = gcs_id;
            pilot_lease_deadline_ = now_ms + HeartbeatTimeoutMs;
            token_nonce_ = next_nonce();
            state_ = State::PilotActive;
            return token_nonce_;
        }
        return std::unexpected(ArbiterError::AlreadyLocked);
    }

    bool process_heartbeat(uint8_t gcs_id, RoleFlags roles, uint32_t now_ms) noexcept {
        if (gcs_id == pilot_gcs_id_ && (static_cast<uint8_t>(roles) & static_cast<uint8_t>(RoleFlags::Pilot))) {
            pilot_lease_deadline_ = now_ms + HeartbeatTimeoutMs;
            if (state_ == State::LinkLost) {
                state_ = State::PilotActive;
            }
            return true;
        }
        if (static_cast<uint8_t>(roles) & static_cast<uint8_t>(RoleFlags::Payload)) {
            payload_gcs_id_ = gcs_id;
        }
        return true;
    }

    [[nodiscard]] std::expected<void, ArbiterError> initiate_handover(uint8_t current_pilot, uint8_t target_gcs, uint32_t now_ms) noexcept {
        if (state_ != State::PilotActive || current_pilot != pilot_gcs_id_) {
            return std::unexpected(ArbiterError::Unauthorized);
        }
        pending_pilot_gcs_id_ = target_gcs;
        handover_deadline_ = now_ms + HandoverTimeoutMs;
        state_ = State::HandoverWaitStick;
        return {};
    }

    [[nodiscard]] std::expected<uint32_t, ArbiterError> confirm_handover_sticks(uint8_t candidate_id, const StickAxes& sticks, uint32_t now_ms) noexcept {
        if (state_ != State::HandoverWaitStick || candidate_id != pending_pilot_gcs_id_) {
            return std::unexpected(ArbiterError::Unauthorized);
        }
        if (now_ms > handover_deadline_) {
            state_ = State::PilotActive;
            pending_pilot_gcs_id_ = 0;
            return std::unexpected(ArbiterError::Timeout);
        }
        if (!sticks.is_neutral()) {
            return std::unexpected(ArbiterError::StickNotNeutral);
        }

        pilot_gcs_id_ = candidate_id;
        pending_pilot_gcs_id_ = 0;
        pilot_lease_deadline_ = now_ms + HeartbeatTimeoutMs;
        token_nonce_ = next_nonce();
        state_ = State::PilotActive;
        return token_nonce_;
    }

    void commander_override(uint8_t /*commander_id*/, uint32_t /*now_ms*/) noexcept {
        state_ = State::CommanderLocked;
        pilot_gcs_id_ = 0;
        pending_pilot_gcs_id_ = 0;
        token_nonce_ = next_nonce();
    }

    [[nodiscard]] bool is_flight_command_allowed(uint8_t src_gcs_id, uint32_t nonce) const noexcept {
        if (state_ != State::PilotActive && state_ != State::HandoverWaitStick) {
            return false;
        }
        return (src_gcs_id == pilot_gcs_id_) && (nonce == token_nonce_);
    }

    void periodic_tick(uint32_t now_ms) noexcept {
        if (state_ == State::PilotActive || state_ == State::HandoverWaitStick) {
            if (now_ms >= pilot_lease_deadline_) {
                state_ = State::LinkLost;
            }
        }
        if (state_ == State::HandoverWaitStick) {
            if (now_ms >= handover_deadline_) {
                state_ = State::PilotActive;
                pending_pilot_gcs_id_ = 0;
            }
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint8_t active_pilot() const noexcept { return pilot_gcs_id_; }

private:
    static uint32_t next_nonce() noexcept {
        static uint32_t seed = 0x900DCAFE;
        seed = seed * 1664525u + 1013904223u;
        return seed;
    }

    uint8_t   pilot_gcs_id_{0};
    uint8_t   payload_gcs_id_{0};
    uint8_t   pending_pilot_gcs_id_{0};
    uint32_t  pilot_lease_deadline_{0};
    uint32_t  handover_deadline_{0};
    uint32_t  token_nonce_{0};
    State     state_{State::Idle};
};

} // namespace auth::arbiter
