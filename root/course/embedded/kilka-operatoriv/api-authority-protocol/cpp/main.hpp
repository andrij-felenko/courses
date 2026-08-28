#pragma once

#include <cstdint>
#include <span>
#include <expected>
#include <string_view>

namespace auth::protocol {

inline constexpr uint8_t  MagicByte             = 0xAA;
inline constexpr uint8_t  ProtocolVersion       = 0x01;
inline constexpr uint32_t HeartbeatTimeoutMs    = 1000;
inline constexpr uint32_t HandoverTimeoutMs     = 5000;
inline constexpr float    DeadbandPercent       = 3.0F;

enum class Role : uint8_t {
    None      = 0x00,
    Monitor   = 0x01,
    Pilot     = 0x02,
    Payload   = 0x04,
    Commander = 0x08
};

[[nodiscard]] constexpr Role operator|(Role lhs, Role rhs) noexcept {
    return static_cast<Role>(static_cast<uint8_t>(lhs) | static_cast<uint8_t>(rhs));
}

[[nodiscard]] constexpr bool has_role(Role mask, Role required) noexcept {
    return (static_cast<uint8_t>(mask) & static_cast<uint8_t>(required)) != 0;
}

enum class StatusCode : uint8_t {
    Ok                  = 0x00,
    Unauthorized        = 0x01,
    TokenAlreadyTaken   = 0x02,
    StickNotNeutral     = 0x03,
    LeaseExpired        = 0x04,
    PriorityTooLow      = 0x05,
    CrcMismatch         = 0x06
};

enum class MessageId : uint16_t {
    Heartbeat        = 0x0080,
    TokenRequest     = 0x0081,
    TokenGrant       = 0x0082,
    TokenRevoke      = 0x0083,
    HandoverOffer    = 0x0084,
    StickCheck       = 0x0085,
    CommanderOverride= 0x0086,
    StatusBroadcast  = 0x0087
};

#pragma pack(push, 1)

struct PacketHeader {
    uint8_t   magic{MagicByte};
    uint8_t   version{ProtocolVersion};
    MessageId msg_id{MessageId::Heartbeat};
    uint8_t   source_id{0};
    uint8_t   target_id{0};
    uint16_t  seq_num{0};
    uint32_t  timestamp_ms{0};
    uint32_t  token_nonce{0};
    uint16_t  payload_len{0};
    uint16_t  crc16{0};
};

struct NormalizedSticks {
    int16_t roll{0};      // Діапазон: -1000 .. +1000
    int16_t pitch{0};     // Діапазон: -1000 .. +1000
    int16_t yaw{0};       // Діапазон: -1000 .. +1000
    int16_t throttle{0};  // Діапазон: 0 .. +1000
    uint8_t is_neutral{0};

    [[nodiscard]] constexpr bool verify_deadband(float tolerance_pct = DeadbandPercent) const noexcept {
        const int16_t limit = static_cast<int16_t>(1000.0F * (tolerance_pct / 100.0F));
        const bool center_neutral = (roll >= -limit && roll <= limit) &&
                                    (pitch >= -limit && pitch <= limit) &&
                                    (yaw >= -limit && yaw <= limit);
        return center_neutral;
    }
};

struct ArbitrationStatus {
    uint8_t  pilot_gcs_id{0};
    uint8_t  payload_gcs_id{0};
    uint8_t  commander_gcs_id{0};
    uint32_t pilot_lease_remaining_ms{0};
    uint8_t  arbitration_state{0};
};

#pragma pack(pop)

} // namespace auth::protocol
