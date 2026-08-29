#include "node.hpp"

#include <algorithm>
#include <utility>

namespace sbo {
namespace {

bool comp_known(Comp c) noexcept {
    return c == Comp::Fc || c == Comp::Esc || c == Comp::Nav;
}

}  // namespace

Node::Node(std::uint8_t id, std::uint32_t seed)
    : id_{id}, rng_{seed ? seed : 0x1234567u} {}

std::uint32_t Node::next_token() {
    // xorshift32: непередбачуваності в межах польоту досить, криптостійкості
    // профіль не обіцяє. Нуль зарезервовано під «замка немає».
    std::uint32_t x = rng_;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    if (x == 0) x = 0xA5A5A5A5u;
    rng_ = x;
    return x;
}

State Node::state() const noexcept {
    if (executing_) return State::Executing;
    return lock_ ? State::Armed : State::Idle;
}

Ms Node::remaining(Ms now) const noexcept {
    if (!lock_ || now >= lock_->deadline) return Ms{0};
    return lock_->deadline - now;
}

void Node::release(Ms now, bool expired) {
    if (expired && lock_) {
        // Пам'ятаємо згорілий токен: запізнілий OPERATE_REQ дістане точну
        // причину TimeoutExpired, а не загальне NotArmed.
        expired_token_ = lock_->token;
    }
    lock_.reset();
    executing_ = false;
    cooldown_until_ = now + kCooldown;
    flags_ &= static_cast<std::uint8_t>(~kFlagArmed);
}

void Node::tick(Ms now) {
    if (lock_ && !executing_ && now >= lock_->deadline) {
        release(now, true);
    }
}

Frame Node::reply(const Frame& req, MsgType type, std::uint32_t token, Ms window,
                  std::optional<Error> reason) {
    Frame r;
    r.seq = seq_++;
    r.type = type;
    r.source = id_;
    r.target = req.source;    // відповідь завжди адресна
    r.comp = req.comp;
    r.state = state();
    r.token = token;
    r.cmd = req.cmd;
    r.window = window;
    if (reason) r.payload.push_back(std::to_underlying(*reason));
    return r;
}

Frame Node::nack(const Frame& req, MsgType type, Error reason) {
    flags_ |= kFlagLastReject;
    return reply(req, type, 0, Ms{0}, reason);
}

std::expected<void, Error> Node::execute(Cmd cmd, std::span<const std::uint8_t> params) {
    if (!act_.healthy) return std::unexpected(Error::HardwareFault);

    switch (cmd) {
        case Cmd::Ping:
        case Cmd::RequestTelemetry:
            return {};
        case Cmd::EmergencyMotorCut:
            act_.motors_live = false;
            act_.armed = false;
            return {};
        case Cmd::ForceDisarm:
            act_.armed = false;
            return {};
        case Cmd::FlightModeOverride:
            if (params.empty()) return std::unexpected(Error::CmdMismatch);
            act_.flight_mode = params.front();
            return {};
        case Cmd::RebootAutopilot:
            act_.reboot_pending = true;
            return {};
        case Cmd::FactoryResetParams:
            act_.params_default = true;
            return {};
        case Cmd::PayloadDropActuate:
            if (act_.payload_dropped) {
                return std::unexpected(Error::HardwareFault);  // скидач порожній
            }
            act_.payload_dropped = true;
            return {};
        default:
            return std::unexpected(Error::CmdMismatch);
    }
}

std::optional<Frame> Node::on_select(const Frame& req, Ms now) {
    if (!is_critical(req.cmd)) {
        // Звичайні команди йдуть напряму — селекція для них безглузда.
        return nack(req, MsgType::SelectNack, Error::CmdMismatch);
    }
    if (!comp_known(req.comp)) {
        return nack(req, MsgType::SelectNack, Error::HardwareFault);
    }
    if (lock_ || executing_) {
        return nack(req, MsgType::SelectNack, Error::Busy);   // сценарій В
    }
    if (now < cooldown_until_) {
        return nack(req, MsgType::SelectNack, Error::Busy);   // T_cooldown
    }
    if (!act_.healthy) {
        return nack(req, MsgType::SelectNack, Error::HardwareFault);
    }

    const Ms window = clamp_window(req.window);
    lock_ = Lock{req.source, req.comp, req.cmd, next_token(), now + window};
    flags_ |= kFlagArmed;
    flags_ &= static_cast<std::uint8_t>(~kFlagLastReject);
    return reply(req, MsgType::SelectAck, lock_->token, window, std::nullopt);
}

std::optional<Frame> Node::on_operate(const Frame& req, Ms now) {
    if (!is_critical(req.cmd)) {
        // Звичайний клас: ні замка, ні токена.
        if (auto done = execute(req.cmd, req.payload); !done) {
            return nack(req, MsgType::OperateNack, done.error());
        }
        return reply(req, MsgType::OperateAck, 0, Ms{0}, std::nullopt);
    }
    if (executing_) {
        return nack(req, MsgType::OperateNack, Error::Busy);
    }
    if (!lock_) {
        // Сценарій Б: токен пульта збігся зі згорілим — кажемо саме про час.
        const Error why = (req.token != 0 && req.token == expired_token_)
                              ? Error::TimeoutExpired
                              : Error::NotArmed;
        return nack(req, MsgType::OperateNack, why);
    }
    if (now >= lock_->deadline) {
        // Пояс на випадок, коли tick не встиг спрацювати між кадрами.
        release(now, true);
        return nack(req, MsgType::OperateNack, Error::TimeoutExpired);
    }
    if (req.source != lock_->owner) {
        return nack(req, MsgType::OperateNack, Error::Busy);
    }
    if (req.token == 0 || req.token != lock_->token) {
        return nack(req, MsgType::OperateNack, Error::InvalidToken);
    }
    if (req.cmd != lock_->cmd || req.comp != lock_->comp) {
        return nack(req, MsgType::OperateNack, Error::CmdMismatch);
    }
    if (req.cmd == Cmd::FactoryResetParams &&
        !(req.payload.size() >= password_.size() &&
          std::ranges::equal(std::span{req.payload}.first(password_.size()), password_))) {
        return nack(req, MsgType::OperateNack, Error::CmdMismatch);
    }

    executing_ = true;                     // таймер знешкодження вже не діє
    const auto done = execute(req.cmd, req.payload);
    release(now, false);                   // після дії автомат одразу в IDLE

    if (!done) {
        return nack(req, MsgType::OperateNack, done.error());
    }
    flags_ &= static_cast<std::uint8_t>(~kFlagLastReject);
    return reply(req, MsgType::OperateAck, 0, Ms{0}, std::nullopt);
}

std::optional<Frame> Node::on_cancel(const Frame& req, Ms now) {
    if (!lock_ && !executing_) {
        // Скасування вільного вузла нешкідливе: так пульт лікує розсинхрон UI.
        return reply(req, MsgType::CancelAck, 0, Ms{0}, std::nullopt);
    }
    if (executing_ || req.source != lock_->owner) {
        // Чужий замок не знімаємо, але квитанцію з причиною даємо.
        flags_ |= kFlagLastReject;
        return reply(req, MsgType::CancelAck, 0, Ms{0}, Error::Busy);
    }
    release(now, false);
    return reply(req, MsgType::CancelAck, 0, Ms{0}, std::nullopt);
}

std::optional<Frame> Node::on_ping(const Frame& req, Ms now) {
    // Токен бачить лише власник замка; решті — нуль.
    const std::uint32_t token =
        (lock_ && req.source == lock_->owner) ? lock_->token : 0u;
    Frame r = reply(req, MsgType::StatusPong, token, remaining(now), std::nullopt);
    r.payload.push_back(flags_);
    return r;
}

std::optional<Frame> Node::handle(std::span<const std::uint8_t> raw, Ms now) {
    const auto parsed = decode(raw);
    if (!parsed) {
        ++rx_errors_;              // битий кадр — в ефір не відповідаємо
        return std::nullopt;
    }
    const Frame& req = *parsed;

    // Спершу зістарюємо замок, аж тоді судимо запит: інакше кадр, що прийшов
    // на мілісекунду пізніше за вікно, виглядав би дійсним.
    tick(now);

    if (req.target != id_ && req.target != kAddrBroadcast) {
        return std::nullopt;       // кадр не нам
    }
    if (req.target == kAddrBroadcast) {
        const bool forbidden = is_critical(req.cmd) ||
                               req.type == MsgType::SelectReq ||
                               req.type == MsgType::CancelReq;
        if (forbidden) {
            // Сценарій Г: причина — BroadcastForbidden, але відповіді в ефір
            // немає: широкомовний NACK від кожного апарата дав би шторм.
            ++security_drops_;
            flags_ |= kFlagLastReject;
            return std::nullopt;
        }
    }

    switch (req.type) {
        case MsgType::SelectReq:  return on_select(req, now);
        case MsgType::OperateReq: return on_operate(req, now);
        case MsgType::CancelReq:  return on_cancel(req, now);
        case MsgType::StatusPing: return on_ping(req, now);
        default:                  return std::nullopt;  // квитанції вузол не обробляє
    }
}

}  // namespace sbo
