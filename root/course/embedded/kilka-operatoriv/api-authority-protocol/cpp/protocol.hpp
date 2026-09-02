#pragma once

#include <chrono>
#include <cstdint>

namespace auth {

using Ms = std::chrono::milliseconds;

// Маркер синхронізації та версія бінарного формату (розділ 2).
inline constexpr std::uint8_t MagicByte       = 0xAA;
inline constexpr std::uint8_t ProtocolVersion = 0x01;
inline constexpr std::uint8_t BroadcastId     = 0xFF;

// Часові вимоги розділу 4.
inline constexpr Ms HeartbeatPeriod{250};
inline constexpr Ms LeaseTimeout{1000};
inline constexpr Ms HandoverTimeout{5000};

// Осі нормалізовано в ±1000, мертва зона ±3 % — це ±30 одиниць.
inline constexpr std::int16_t AxisFullScale = 1000;
inline constexpr std::int16_t DeadbandUnits = 30;

enum class Role : std::uint8_t {
    None      = 0x00,
    Monitor   = 0x01,
    Pilot     = 0x02,
    Payload   = 0x04,
    Commander = 0x08
};

[[nodiscard]] constexpr Role operator|(Role lhs, Role rhs) noexcept {
    return static_cast<Role>(static_cast<std::uint8_t>(lhs) | static_cast<std::uint8_t>(rhs));
}

[[nodiscard]] constexpr bool has_role(Role mask, Role required) noexcept {
    return (static_cast<std::uint8_t>(mask) & static_cast<std::uint8_t>(required)) != 0;
}

enum class StatusCode : std::uint8_t {
    Ok                = 0x00,
    Unauthorized      = 0x01,
    TokenAlreadyTaken = 0x02,
    StickNotNeutral   = 0x03,
    LeaseExpired      = 0x04,
    PriorityTooLow    = 0x05,
    CrcMismatch       = 0x06,
    // Помилки рівня кадру: до розбору корисного навантаження.
    BadMagic          = 0x07,
    BadVersion        = 0x08,
    BadLength         = 0x09,
    Replay            = 0x0A
};

enum class MessageId : std::uint16_t {
    Heartbeat         = 0x0080,
    TokenRequest      = 0x0081,
    TokenGrant        = 0x0082,
    TokenRevoke       = 0x0083,
    HandoverOffer     = 0x0084,
    StickCheck        = 0x0085,
    CommanderOverride = 0x0086,
    StatusBroadcast   = 0x0087
};

// Стани скінченного автомата арбітра (розділ 5).
enum class ArbitrationState : std::uint8_t {
    Idle              = 0,
    PilotActive       = 1,
    HandoverWaitStick = 2,
    LinkLost          = 3,
    CommanderLocked   = 4
};

// Що арбітр наказує автопілоту, коли повноважень не лишилося.
enum class Failsafe : std::uint8_t { None = 0, Loiter = 1, ReturnToLaunch = 2, Brake = 3 };

enum class RevokeReason : std::uint8_t { LeaseExpired = 0, Handover = 1, CommanderOverride = 2 };

enum class OverrideAction : std::uint8_t { Hold = 0, ReturnToLaunch = 1, Release = 2 };

#pragma pack(push, 1)

// Заголовок кадру: 20 байтів на дроті — рівно сума полів із діаграми
// розділу 2. Порядок байтів Little-Endian, кладе на дріт auth::encode.
struct PacketHeader {
    std::uint8_t  magic{MagicByte};
    std::uint8_t  version{ProtocolVersion};
    MessageId     msg_id{MessageId::Heartbeat};
    std::uint8_t  source_id{0};
    std::uint8_t  target_id{0};
    std::uint16_t seq_num{0};
    std::uint32_t timestamp_ms{0};
    std::uint32_t token_nonce{0};
    std::uint16_t payload_len{0};
    std::uint16_t crc16{0};
};

struct Heartbeat {
    Role          active_roles{Role::Monitor};
    std::uint16_t lease_requested_ms{static_cast<std::uint16_t>(LeaseTimeout.count())};
};

// target_gcs_id != 0 у запиті ролі пілота від діючого пілота означає не
// захоплення токена, а ініціацію передачі зміни на вказану станцію.
struct TokenRequest {
    Role          requested_role{Role::Monitor};
    std::uint8_t  target_gcs_id{0};
    std::uint32_t auth_token{0};
};

// Той самий кадр несе й відмову: status != Ok, granted_role == None.
struct TokenGrant {
    Role          granted_role{Role::None};
    StatusCode    status{StatusCode::Ok};
    std::uint16_t lease_ms{0};
    std::uint32_t token_nonce{0};
};

struct TokenRevoke {
    Role         revoked_role{Role::None};
    RevokeReason reason{RevokeReason::LeaseExpired};
    std::uint8_t gcs_id{0};
};

// throttle_target — поточний газ борту, під який змінний пілот вирівнює стік.
struct HandoverOffer {
    std::uint8_t  from_gcs_id{0};
    std::uint8_t  to_gcs_id{0};
    std::uint16_t timeout_ms{static_cast<std::uint16_t>(HandoverTimeout.count())};
    std::int16_t  throttle_target{0};
};

struct NormalizedSticks {
    std::int16_t roll{0};      // Діапазон: -1000 .. +1000
    std::int16_t pitch{0};     // Діапазон: -1000 .. +1000
    std::int16_t yaw{0};       // Діапазон: -1000 .. +1000
    std::int16_t throttle{0};  // Діапазон: 0 .. +1000
    std::uint8_t is_neutral{0};  // Думка станції; борт рахує сам

    [[nodiscard]] constexpr bool centered(std::int16_t band = DeadbandUnits) const noexcept {
        return roll >= -band && roll <= band &&
               pitch >= -band && pitch <= band &&
               yaw >= -band && yaw <= band;
    }

    [[nodiscard]] constexpr bool matches_throttle(std::int16_t vehicle,
                                                  std::int16_t band = DeadbandUnits) const noexcept {
        const int diff = static_cast<int>(throttle) - static_cast<int>(vehicle);
        return (diff < 0 ? -diff : diff) <= band;
    }
};

struct CommanderOverride {
    std::uint8_t   override_reason{0};
    OverrideAction action_command{OverrideAction::Hold};
    std::uint32_t  signature_hash{0};
};

struct ArbitrationStatus {
    std::uint8_t     pilot_gcs_id{0};
    std::uint8_t     payload_gcs_id{0};
    std::uint8_t     commander_gcs_id{0};
    std::uint32_t    pilot_lease_remaining_ms{0};
    ArbitrationState state{ArbitrationState::Idle};
};

#pragma pack(pop)

// Тип повідомлення сам знає свій ідентифікатор — кодувальнику не треба
// передавати msg_id окремо, а розбір звіряє його автоматично.
template <class T> struct MessageTraits;

template <> struct MessageTraits<Heartbeat>         { static constexpr MessageId id = MessageId::Heartbeat; };
template <> struct MessageTraits<TokenRequest>      { static constexpr MessageId id = MessageId::TokenRequest; };
template <> struct MessageTraits<TokenGrant>        { static constexpr MessageId id = MessageId::TokenGrant; };
template <> struct MessageTraits<TokenRevoke>       { static constexpr MessageId id = MessageId::TokenRevoke; };
template <> struct MessageTraits<HandoverOffer>     { static constexpr MessageId id = MessageId::HandoverOffer; };
template <> struct MessageTraits<NormalizedSticks>  { static constexpr MessageId id = MessageId::StickCheck; };
template <> struct MessageTraits<CommanderOverride> { static constexpr MessageId id = MessageId::CommanderOverride; };
template <> struct MessageTraits<ArbitrationStatus> { static constexpr MessageId id = MessageId::StatusBroadcast; };

}  // namespace auth
