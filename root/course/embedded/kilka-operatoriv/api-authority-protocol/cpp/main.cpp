// Наскрізний прогін протоколу арбітражу на модельному годиннику:
// борт із арбітром і чотири станції в спільній радіомережі.

#include <array>
#include <format>
#include <iostream>
#include <stdexcept>
#include <string_view>

#include "arbiter.hpp"
#include "frame.hpp"

namespace {

using namespace auth;

constexpr std::uint8_t  kFcuId        = 1;
constexpr std::uint8_t  kPilot        = 11;
constexpr std::uint8_t  kPayload      = 12;
constexpr std::uint8_t  kRelief       = 13;
constexpr std::uint8_t  kCommander    = 14;
constexpr std::uint32_t kCommanderKey = 0xC0FFEE01;

struct Station {
    std::uint8_t  id{0};
    std::uint16_t seq{0};
    std::uint32_t nonce{0};  // видане бортом одноразове число
    Role          role{Role::None};
};

std::array<Station, 4> g_stations{Station{kPilot}, Station{kPayload}, Station{kRelief},
                                  Station{kCommander}};
Ms           g_now{0};
std::int16_t g_offer_throttle{0};

Station& station(std::uint8_t id) {
    for (Station& s : g_stations) {
        if (s.id == id) {
            return s;
        }
    }
    throw std::invalid_argument{"невідома станція"};
}

std::string_view status_name(StatusCode st) {
    switch (st) {
        case StatusCode::Ok:                return "OK";
        case StatusCode::Unauthorized:      return "UNAUTHORIZED";
        case StatusCode::TokenAlreadyTaken: return "TOKEN_ALREADY_TAKEN";
        case StatusCode::StickNotNeutral:   return "STICK_NOT_NEUTRAL";
        case StatusCode::LeaseExpired:      return "LEASE_EXPIRED";
        case StatusCode::PriorityTooLow:    return "PRIORITY_TOO_LOW";
        case StatusCode::CrcMismatch:       return "CRC_MISMATCH";
        case StatusCode::BadMagic:          return "BAD_MAGIC";
        case StatusCode::BadVersion:        return "BAD_VERSION";
        case StatusCode::BadLength:         return "BAD_LENGTH";
        case StatusCode::Replay:            return "REPLAY";
    }
    return "?";
}

std::string_view state_name(ArbitrationState s) {
    switch (s) {
        case ArbitrationState::Idle:              return "IDLE";
        case ArbitrationState::PilotActive:       return "PILOT_ACTIVE";
        case ArbitrationState::HandoverWaitStick: return "HANDOVER_WAIT_STICK";
        case ArbitrationState::LinkLost:          return "LINK_LOST";
        case ArbitrationState::CommanderLocked:   return "COMMANDER_LOCKED";
    }
    return "?";
}

std::string_view result_name(const std::expected<void, StatusCode>& r) {
    return r ? status_name(StatusCode::Ok) : status_name(r.error());
}

// Усе, що борт випромінює, чують усі станції — це спільна радіомережа.
void on_board_emit(std::span<const std::byte> raw) {
    const auto decoded = decode(raw);
    if (!decoded) {
        std::cout << "      [ефір] пошкоджений кадр борту\n";
        return;
    }
    const Frame& f = *decoded;

    switch (f.header.msg_id) {
        case MessageId::TokenGrant: {
            const auto g = body_as<TokenGrant>(f).value();
            if (g.status == StatusCode::Ok) {
                Station& s = station(f.header.target_id);
                s.nonce    = g.token_nonce;
                s.role     = g.granted_role;
                std::cout << std::format(
                    "      GRANT  → GCS#{}  роль=0x{:02X}  оренда={} мс  nonce=0x{:08X}\n",
                    f.header.target_id, static_cast<int>(g.granted_role), g.lease_ms,
                    g.token_nonce);
            } else {
                std::cout << std::format("      ВІДМОВА → GCS#{}  причина={}\n",
                                         f.header.target_id, status_name(g.status));
            }
            break;
        }
        case MessageId::TokenRevoke: {
            const auto r = body_as<TokenRevoke>(f).value();
            Station&   s = station(f.header.target_id);
            s.nonce      = 0;
            s.role       = Role::None;
            std::cout << std::format("      REVOKE → GCS#{}  роль=0x{:02X}  причина={}\n",
                                     f.header.target_id, static_cast<int>(r.revoked_role),
                                     static_cast<int>(r.reason));
            break;
        }
        case MessageId::HandoverOffer: {
            const auto o     = body_as<HandoverOffer>(f).value();
            g_offer_throttle = o.throttle_target;
            std::cout << std::format("      OFFER  → GCS#{}  від GCS#{}  вікно={} мс  газ={}\n",
                                     o.to_gcs_id, o.from_gcs_id, o.timeout_ms,
                                     o.throttle_target);
            break;
        }
        case MessageId::StatusBroadcast: {
            const auto s = body_as<ArbitrationStatus>(f).value();
            std::cout << std::format(
                "      STATUS: пілот={} навантаження={} командир={} оренда={} мс стан={}\n",
                s.pilot_gcs_id, s.payload_gcs_id, s.commander_gcs_id,
                s.pilot_lease_remaining_ms, state_name(s.state));
            break;
        }
        default:
            break;
    }
}

Arbiter g_fcu{kFcuId, kCommanderKey, on_board_emit};

// Станція складає кадр і кладе його в ефір; борт відповідає негайно.
template <class T>
std::expected<void, StatusCode> send_from(Station& s, const T& body) {
    PacketHeader header{};
    header.source_id    = s.id;
    header.target_id    = kFcuId;
    header.seq_num      = ++s.seq;
    header.timestamp_ms = static_cast<std::uint32_t>(g_now.count());
    header.token_nonce  = s.nonce;

    return g_fcu.handle(encode_message(header, body), g_now);
}

std::expected<void, StatusCode> request_role(Station& s, Role role, std::uint8_t target = 0,
                                             std::uint32_t key = 0) {
    return send_from(s, TokenRequest{.requested_role = role,
                                     .target_gcs_id  = target,
                                     .auth_token     = key});
}

void heartbeat(Station& s) {
    (void)send_from(s, Heartbeat{.active_roles       = s.role,
                                 .lease_requested_ms = static_cast<std::uint16_t>(
                                     LeaseTimeout.count())});
}

void advance(Ms dt) {
    g_now += dt;
    switch (g_fcu.tick(g_now)) {
        case Failsafe::Loiter:         std::cout << "      >>> автопілоту: LOITER\n"; break;
        case Failsafe::ReturnToLaunch: std::cout << "      >>> автопілоту: RTL\n"; break;
        case Failsafe::Brake:          std::cout << "      >>> автопілоту: BRAKE\n"; break;
        case Failsafe::None:           break;
    }
}

// Кадр стіків на 50 Гц: проходить лише крізь фільтр повноважень.
void push_control(const Station& s, Role plane, std::string_view what) {
    const bool ok = g_fcu.accept_control(s.id, s.nonce, plane, g_now);
    std::cout << std::format("      GCS#{} {} → {}\n", s.id, what,
                             ok ? "ВИКОНАНО" : "ВІДКИНУТО");
}

}  // namespace

int main() {
    g_fcu.set_vehicle_throttle(620);

    std::cout << "=== 1. Розбір ролей ===\n";
    std::cout << std::format("  GCS#{} просить пілотування: {}\n", kPilot,
                             result_name(request_role(station(kPilot), Role::Pilot)));
    std::cout << std::format("  GCS#{} просить навантаження: {}\n", kPayload,
                             result_name(request_role(station(kPayload), Role::Payload)));

    std::cout << "\n=== 2. Оператор навантаження хоче доворот носа на ціль ===\n";
    std::cout << std::format("  запит токена пілота: {}\n",
                             result_name(request_role(station(kPayload), Role::Pilot)));
    push_control(station(kPilot), Role::Pilot, "крен -20 град");
    push_control(station(kPayload), Role::Pilot, "крен +15 град (авто-ціль)");
    push_control(station(kPayload), Role::Payload, "поворот підвісу");

    std::cout << "\n=== 3. Оренда живе на серцебитті ===\n";
    for (int i = 0; i < 4; ++i) {
        advance(Ms{250});
        heartbeat(station(kPilot));
        heartbeat(station(kPayload));
    }
    push_control(station(kPilot), Role::Pilot, "крен -20 град");

    std::cout << "\n=== 4. Пульт пілота замовк на 1200 мс ===\n";
    advance(Ms{1200});
    push_control(station(kPilot), Role::Pilot, "крен -20 град");
    std::cout << std::format("  вільний токен бере той самий пульт: {}\n",
                             result_name(request_role(station(kPilot), Role::Pilot)));

    std::cout << std::format("\n=== 5. Передача зміни на GCS#{} ===\n", kRelief);
    std::cout << std::format("  ініціація: {}\n",
                             result_name(request_role(station(kPilot), Role::Pilot, kRelief)));

    NormalizedSticks sticks{};
    sticks.roll       = 120;  // стік відхилено
    sticks.throttle   = g_offer_throttle;
    sticks.is_neutral = 1;    // станція бреше, борт перевіряє
    std::cout << std::format("  звірка з відхиленим стіком: {}\n",
                             result_name(send_from(station(kRelief), sticks)));

    sticks.roll = 8;  // у межах ±3 %
    std::cout << std::format("  звірка з нейтраллю: {}\n",
                             result_name(send_from(station(kRelief), sticks)));
    push_control(station(kPilot), Role::Pilot, "крен -20 град (старий nonce)");
    push_control(station(kRelief), Role::Pilot, "крен -20 град");

    std::cout << "\n=== 6. Змінний пілот не відповів ===\n";
    std::cout << std::format(
        "  ініціація на GCS#{}: {}\n", kPayload,
        result_name(request_role(station(kRelief), Role::Pilot, kPayload)));
    advance(Ms{5100});
    std::cout << std::format("  токен лишився в GCS#{}\n", kRelief);

    std::cout << "\n=== 7. Перехоплення командиром ===\n";
    Station& cmd = station(kCommander);
    std::cout << std::format(
        "  токен командира: {}\n",
        result_name(request_role(cmd, Role::Commander, 0, kCommanderKey)));

    std::cout << std::format(
        "  перехоплення з чужим підписом: {}\n",
        result_name(send_from(cmd, CommanderOverride{.override_reason = 0,
                                                     .action_command  = OverrideAction::Hold,
                                                     .signature_hash  = 0xDEADBEEF})));

    // Підпис накриває наступний seq і поточний час — повторити кадр не вийде.
    const std::uint32_t signature =
        sign_override(kCommanderKey, cmd.id, static_cast<std::uint16_t>(cmd.seq + 1),
                      static_cast<std::uint32_t>(g_now.count()));
    std::cout << std::format(
        "  перехоплення з валідним підписом: {}\n",
        result_name(send_from(cmd, CommanderOverride{.override_reason = 0,
                                                     .action_command  = OverrideAction::Hold,
                                                     .signature_hash  = signature})));
    advance(Ms{0});
    push_control(station(kRelief), Role::Pilot, "крен -20 град");
    std::cout << std::format("  спроба взяти токен під блокуванням: {}\n",
                             result_name(request_role(station(kRelief), Role::Pilot)));

    return 0;
}
