#include "arbiter.hpp"

#include <algorithm>
#include <utility>

namespace auth {
namespace {

// Оренду просить станція, але стелю ставить борт.
[[nodiscard]] Ms clamp_lease(std::uint16_t requested) noexcept {
    if (requested == 0) {
        return LeaseTimeout;
    }
    return std::clamp(Ms{requested}, HeartbeatPeriod, LeaseTimeout);
}

}  // namespace

Arbiter::Arbiter(std::uint8_t self_id, std::uint32_t commander_key, Emit emit)
    : self_id_{self_id}, commander_key_{commander_key}, emit_{std::move(emit)} {}

std::uint32_t Arbiter::next_nonce() {
    std::uint32_t value = 0;
    // Нуль не видаємо: нуль означає «токена немає».
    while (value == 0) {
        value = static_cast<std::uint32_t>(rng_());
    }
    return value;
}

template <class T>
void Arbiter::send(std::uint8_t target, const T& body, Ms now, std::uint32_t nonce) {
    PacketHeader header{};
    header.source_id    = self_id_;
    header.target_id    = target;
    header.seq_num      = ++tx_seq_;
    header.timestamp_ms = static_cast<std::uint32_t>(now.count());
    header.token_nonce  = nonce;

    const std::vector<std::byte> raw = encode_message(header, body);
    if (!raw.empty() && emit_) {
        emit_(raw);
    }
}

void Arbiter::reply_grant(std::uint8_t target, Role role, StatusCode status,
                          std::uint32_t nonce, Ms now) {
    const TokenGrant grant{.granted_role = role,
                           .status       = status,
                           .lease_ms     = static_cast<std::uint16_t>(LeaseTimeout.count()),
                           .token_nonce  = nonce};
    send(target, grant, now, nonce);
}

void Arbiter::send_revoke(std::uint8_t target, Role role, RevokeReason reason, Ms now) {
    send(target, TokenRevoke{.revoked_role = role, .reason = reason, .gcs_id = target}, now);
}

void Arbiter::broadcast_status(Ms now) {
    send(BroadcastId, status(now), now);
}

ArbitrationStatus Arbiter::status(Ms now) const noexcept {
    const bool pilot_ok = pilot_.active(now);
    return ArbitrationStatus{
        .pilot_gcs_id     = pilot_ok ? pilot_.gcs : std::uint8_t{0},
        .payload_gcs_id   = payload_.active(now) ? payload_.gcs : std::uint8_t{0},
        .commander_gcs_id = commander_.gcs,
        .pilot_lease_remaining_ms =
            pilot_ok ? static_cast<std::uint32_t>((pilot_.lease_deadline - now).count()) : 0u,
        .state = state_};
}

// Захист від повтору: номер послідовності мусить зростати. Порівняння
// різниці зі знаком витримує переповнення 16-бітного лічильника.
bool Arbiter::seq_ok(std::uint8_t gcs, std::uint16_t seq) {
    const auto it = last_seq_.find(gcs);
    if (it == last_seq_.end()) {
        last_seq_.emplace(gcs, seq);
        return true;
    }
    if (static_cast<std::int16_t>(seq - it->second) <= 0) {
        return false;
    }
    it->second = seq;
    return true;
}

std::expected<void, StatusCode> Arbiter::handle(std::span<const std::byte> raw, Ms now) {
    const auto decoded = decode(raw);
    if (!decoded) {
        // Початок заголовка стабільний між версіями, тож відправника видно
        // навіть у несумісному кадрі — і йому можна відповісти.
        if (decoded.error() == StatusCode::BadVersion && raw.size() >= 5) {
            reply_grant(std::to_integer<std::uint8_t>(raw[4]), Role::None,
                        StatusCode::BadVersion, 0, now);
        }
        return std::unexpected(decoded.error());
    }

    const Frame& f = *decoded;
    if (f.header.target_id != self_id_ && f.header.target_id != BroadcastId) {
        return {};  // кадр не нам: у спільній мережі це норма
    }
    if (!seq_ok(f.header.source_id, f.header.seq_num)) {
        return std::unexpected(StatusCode::Replay);
    }

    switch (f.header.msg_id) {
        case MessageId::Heartbeat:         return on_heartbeat(f, now);
        case MessageId::TokenRequest:      return on_token_request(f, now);
        case MessageId::StickCheck:        return on_stick_check(f, now);
        case MessageId::CommanderOverride: return on_override(f, now);
        default:
            // Решта ідентифікаторів — напрямок FCU→GCS, від станції їх не буває.
            return std::unexpected(StatusCode::Unauthorized);
    }
}

std::expected<void, StatusCode> Arbiter::on_heartbeat(const Frame& f, Ms now) {
    const auto body = body_as<Heartbeat>(f);
    if (!body) {
        return std::unexpected(body.error());
    }
    const Ms lease = clamp_lease(body->lease_requested_ms);

    for (Token* token : {&pilot_, &payload_, &commander_}) {
        if (token->gcs == f.header.source_id && token->nonce == f.header.token_nonce &&
            token->nonce != 0) {
            token->lease_deadline = now + lease;
            return {};
        }
    }

    // Серцебиття з мертвим nonce: станція вважає себе володарем, борт — ні.
    // Кажемо їй правду, щоб вона перезапросила токен, а не гадала.
    if (has_role(body->active_roles, Role::Pilot) ||
        has_role(body->active_roles, Role::Payload)) {
        send_revoke(f.header.source_id, Role::None, RevokeReason::LeaseExpired, now);
        return std::unexpected(StatusCode::LeaseExpired);
    }
    return {};  // спостерігач просто підтверджує канал
}

std::expected<void, StatusCode> Arbiter::grant_exclusive(Token& token, Role role,
                                                         const Frame& f, Ms now) {
    if (token.active(now) && token.gcs != f.header.source_id) {
        reply_grant(f.header.source_id, Role::None, StatusCode::TokenAlreadyTaken, 0, now);
        return std::unexpected(StatusCode::TokenAlreadyTaken);
    }

    token.gcs            = f.header.source_id;
    token.nonce          = next_nonce();
    token.lease_deadline = now + LeaseTimeout;
    if (role == Role::Pilot) {
        state_ = ArbitrationState::PilotActive;
    }

    reply_grant(token.gcs, role, StatusCode::Ok, token.nonce, now);
    broadcast_status(now);
    return {};
}

std::expected<void, StatusCode> Arbiter::start_handover(const Frame& f, std::uint8_t target,
                                                        Ms now) {
    if (handover_) {
        reply_grant(f.header.source_id, Role::None, StatusCode::TokenAlreadyTaken, 0, now);
        return std::unexpected(StatusCode::TokenAlreadyTaken);
    }
    if (target == 0 || target == BroadcastId || target == pilot_.gcs) {
        reply_grant(f.header.source_id, Role::None, StatusCode::Unauthorized, 0, now);
        return std::unexpected(StatusCode::Unauthorized);
    }

    handover_ = Handover{.from = pilot_.gcs, .to = target, .deadline = now + HandoverTimeout};
    state_    = ArbitrationState::HandoverWaitStick;

    send(target,
         HandoverOffer{.from_gcs_id     = handover_->from,
                       .to_gcs_id       = target,
                       .timeout_ms      = static_cast<std::uint16_t>(HandoverTimeout.count()),
                       .throttle_target = vehicle_throttle_},
         now);
    broadcast_status(now);
    return {};
}

std::expected<void, StatusCode> Arbiter::on_token_request(const Frame& f, Ms now) {
    const auto body = body_as<TokenRequest>(f);
    if (!body) {
        return std::unexpected(body.error());
    }

    // Командирський токен видається лише під спільний ключ.
    if (body->requested_role == Role::Commander) {
        if (body->auth_token != commander_key_) {
            reply_grant(f.header.source_id, Role::None, StatusCode::Unauthorized, 0, now);
            return std::unexpected(StatusCode::Unauthorized);
        }
        commander_.gcs            = f.header.source_id;
        commander_.nonce          = next_nonce();
        commander_.lease_deadline = now + LeaseTimeout;
        reply_grant(commander_.gcs, Role::Commander, StatusCode::Ok, commander_.nonce, now);
        broadcast_status(now);
        return {};
    }

    // Поки борт замкнено командиром, чужі запити не проходять.
    if (state_ == ArbitrationState::CommanderLocked && f.header.source_id != commander_.gcs) {
        reply_grant(f.header.source_id, Role::None, StatusCode::PriorityTooLow, 0, now);
        return std::unexpected(StatusCode::PriorityTooLow);
    }

    switch (body->requested_role) {
        case Role::Monitor:
            // Спостерігач не ексклюзивний: токен видається кожному охочому.
            reply_grant(f.header.source_id, Role::Monitor, StatusCode::Ok, next_nonce(), now);
            return {};

        case Role::Pilot:
            if (body->target_gcs_id != 0 && f.header.source_id == pilot_.gcs &&
                pilot_.active(now)) {
                if (f.header.token_nonce != pilot_.nonce) {
                    reply_grant(f.header.source_id, Role::None, StatusCode::Unauthorized, 0, now);
                    return std::unexpected(StatusCode::Unauthorized);
                }
                return start_handover(f, body->target_gcs_id, now);
            }
            if (handover_) {
                reply_grant(f.header.source_id, Role::None, StatusCode::TokenAlreadyTaken, 0, now);
                return std::unexpected(StatusCode::TokenAlreadyTaken);
            }
            return grant_exclusive(pilot_, Role::Pilot, f, now);

        case Role::Payload:
            return grant_exclusive(payload_, Role::Payload, f, now);

        default:
            reply_grant(f.header.source_id, Role::None, StatusCode::Unauthorized, 0, now);
            return std::unexpected(StatusCode::Unauthorized);
    }
}

std::expected<void, StatusCode> Arbiter::on_stick_check(const Frame& f, Ms now) {
    if (!handover_ || f.header.source_id != handover_->to) {
        reply_grant(f.header.source_id, Role::None, StatusCode::Unauthorized, 0, now);
        return std::unexpected(StatusCode::Unauthorized);
    }

    const auto sticks = body_as<NormalizedSticks>(f);
    if (!sticks) {
        return std::unexpected(sticks.error());
    }

    // Прапорець is_neutral — думка станції; борт рахує сам. Довіритися
    // чужому «в мене все по нулях» означає віддати кермо відхиленим стікам.
    if (!sticks->centered() || !sticks->matches_throttle(vehicle_throttle_)) {
        reply_grant(f.header.source_id, Role::None, StatusCode::StickNotNeutral, 0, now);
        return std::unexpected(StatusCode::StickNotNeutral);
    }

    // Атомарний світч: старий nonce вмирає тим самим присвоєнням, яким
    // народжується новий, — проміжного стану «керма ні в кого» немає.
    const std::uint8_t old_pilot = pilot_.gcs;
    pilot_.gcs            = handover_->to;
    pilot_.nonce          = next_nonce();
    pilot_.lease_deadline = now + LeaseTimeout;
    state_                = ArbitrationState::PilotActive;
    handover_.reset();

    reply_grant(pilot_.gcs, Role::Pilot, StatusCode::Ok, pilot_.nonce, now);
    if (old_pilot != 0) {
        send_revoke(old_pilot, Role::Pilot, RevokeReason::Handover, now);
    }
    broadcast_status(now);
    return {};
}

std::expected<void, StatusCode> Arbiter::on_override(const Frame& f, Ms now) {
    const auto body = body_as<CommanderOverride>(f);
    if (!body) {
        return std::unexpected(body.error());
    }

    const std::uint32_t expected = sign_override(commander_key_, f.header.source_id,
                                                 f.header.seq_num, f.header.timestamp_ms);
    if (body->signature_hash != expected) {
        reply_grant(f.header.source_id, Role::None, StatusCode::Unauthorized, 0, now);
        return std::unexpected(StatusCode::Unauthorized);
    }

    commander_.gcs            = f.header.source_id;
    commander_.nonce          = next_nonce();
    commander_.lease_deadline = now + LeaseTimeout;

    if (body->action_command == OverrideAction::Release) {
        // Командир сам знімає блокування: токени лишаються вільними.
        state_            = ArbitrationState::Idle;
        pending_failsafe_ = Failsafe::None;
        reply_grant(commander_.gcs, Role::Commander, StatusCode::Ok, commander_.nonce, now);
        broadcast_status(now);
        return {};
    }

    // Перехоплення рве і незавершену передачу зміни.
    if (pilot_.gcs != 0) {
        send_revoke(pilot_.gcs, Role::Pilot, RevokeReason::CommanderOverride, now);
    }
    if (payload_.gcs != 0) {
        send_revoke(payload_.gcs, Role::Payload, RevokeReason::CommanderOverride, now);
    }
    pilot_.clear();
    payload_.clear();
    handover_.reset();
    state_            = ArbitrationState::CommanderLocked;
    pending_failsafe_ = body->action_command == OverrideAction::ReturnToLaunch
                            ? Failsafe::ReturnToLaunch
                            : Failsafe::Brake;

    reply_grant(commander_.gcs, Role::Commander, StatusCode::Ok, commander_.nonce, now);
    broadcast_status(now);
    return {};
}

Failsafe Arbiter::tick(Ms now) {
    // Прострочена оренда пілота: стіки глухнуть, автопілот іде в LOITER,
    // а токен лишається вільним — резервний пульт бере його негайно.
    if (pilot_.gcs != 0 && !pilot_.active(now)) {
        send_revoke(pilot_.gcs, Role::Pilot, RevokeReason::LeaseExpired, now);
        pilot_.clear();
        handover_.reset();
        if (state_ != ArbitrationState::CommanderLocked) {
            state_            = ArbitrationState::LinkLost;
            pending_failsafe_ = Failsafe::Loiter;
        }
        broadcast_status(now);
    }

    if (payload_.gcs != 0 && !payload_.active(now)) {
        send_revoke(payload_.gcs, Role::Payload, RevokeReason::LeaseExpired, now);
        payload_.clear();
        broadcast_status(now);
    }

    // Змінний пілот не відповів за п'ять секунд — токен лишається старому.
    if (handover_ && now >= handover_->deadline) {
        const std::uint8_t declined = handover_->to;
        handover_.reset();
        state_ = ArbitrationState::PilotActive;
        send_revoke(declined, Role::None, RevokeReason::Handover, now);
        broadcast_status(now);
    }

    return std::exchange(pending_failsafe_, Failsafe::None);
}

bool Arbiter::accept_control(std::uint8_t source_id, std::uint32_t nonce, Role plane,
                             Ms now) const noexcept {
    if (nonce == 0) {
        return false;
    }
    if (plane == Role::Pilot) {
        if (state_ == ArbitrationState::CommanderLocked) {
            return false;
        }
        return pilot_.active(now) && pilot_.gcs == source_id && pilot_.nonce == nonce;
    }
    if (plane == Role::Payload) {
        return payload_.active(now) && payload_.gcs == source_id && payload_.nonce == nonce;
    }
    // Монітор керувати не може за означенням: deny-by-default.
    return false;
}

}  // namespace auth
