// target_engine.cpp — автомат Select-Before-Operate на борту.
#include "sbo/target_engine.hpp"

#include <algorithm>

namespace sbo {
namespace {
constexpr std::chrono::microseconds kExecPulse{10};
constexpr std::chrono::microseconds kDropPulse{50};
}  // namespace

TargetEngine::TargetEngine(NodeId self, Board& board, std::uint32_t seed) noexcept
    : self_(self), board_(board), prng_seed_(seed ^ 0xDEADBEEFu) {
    board_.diag_level(DiagLine::Armed, false);
}

Token TargetEngine::next_token(TimePoint now) noexcept {
    const auto stamp = static_cast<std::uint32_t>(
        std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count());
    prng_seed_ = prng_seed_ * 1664525u + 1013904223u + (stamp << 3);
    const std::uint32_t value = prng_seed_ >> 1;   // молодші біти LCG надто регулярні
    return Token{value != 0 ? value : 0xA5A55A5Au};
}

void TargetEngine::disarm() noexcept {
    if (state_ == State::Armed) {
        board_.diag_level(DiagLine::Armed, false);
    }
    state_          = State::Idle;
    active_token_   = Token{};
    locked_command_ = CommandCode{};
    locked_source_  = NodeId{};
    arm_expiry_     = TimePoint{};
}

bool TargetEngine::tick(TimePoint now) noexcept {
    if (state_ != State::Armed || now < arm_expiry_) {
        return false;
    }
    disarm();
    ++timeout_count_;
    return true;
}

Frame TargetEngine::response(const Frame& rx, MessageType type) const noexcept {
    Frame tx{};
    tx.seq       = rx.seq;
    tx.type      = type;
    tx.source    = self_;
    tx.target    = rx.source;
    tx.component = rx.component;
    tx.command   = rx.command;
    tx.state     = state_;
    return tx;
}

Frame TargetEngine::nack(const Frame& rx, MessageType type, Error err) noexcept {
    Frame tx = response(rx, type);
    tx.payload[0]  = static_cast<std::uint8_t>(err);   // причину оператор побачить у пульті
    tx.payload_len = 1;
    ++reject_count_;
    return tx;
}

std::expected<Frame, Error> TargetEngine::process(const Frame& rx, TimePoint now) noexcept {
    // Строгий unicast: критична дія широкомовним кадром не проходить ніколи.
    if (rx.target.is_broadcast()) {
        board_.diag_pulse(DiagLine::SecurityDrop, kDropPulse);
        ++reject_count_;
        return std::unexpected(Error::BroadcastForbidden);
    }
    if (rx.target != self_) {
        return std::unexpected(Error::ForeignTarget);   // сусідній апарат — мовчимо
    }

    const bool expired = tick(now);

    switch (rx.type) {
    case MessageType::SelectReq: {
        if (state_ == State::Executing ||
            (state_ == State::Armed && locked_source_ != rx.source)) {
            return nack(rx, MessageType::SelectNack, Error::Busy);
        }

        const auto window = std::clamp(rx.timeout.count() > 0 ? rx.timeout : kDefaultWindow,
                                       std::chrono::milliseconds{1}, kMaxWindow);
        state_          = State::Armed;
        locked_source_  = rx.source;
        locked_command_ = rx.command;
        active_token_   = next_token(now);
        arm_expiry_     = now + window;
        ++select_count_;
        board_.diag_level(DiagLine::Armed, true);

        Frame tx   = response(rx, MessageType::SelectAck);
        tx.token   = active_token_;
        tx.timeout = window;
        return tx;
    }

    case MessageType::OperateReq: {
        if (state_ != State::Armed) {
            const Error why = expired                    ? Error::TimeoutExpired
                              : state_ == State::Executing ? Error::Busy
                                                           : Error::NotArmed;
            return nack(rx, MessageType::OperateNack, why);
        }
        if (rx.source != locked_source_) {
            board_.diag_pulse(DiagLine::SecurityDrop, kDropPulse);
            disarm();
            return nack(rx, MessageType::OperateNack, Error::SourceMismatch);
        }
        if (rx.token != active_token_) {
            // Підставлений або запізнілий токен: знімаємо замок негайно.
            board_.diag_pulse(DiagLine::SecurityDrop, kDropPulse);
            disarm();
            return nack(rx, MessageType::OperateNack, Error::InvalidToken);
        }
        if (rx.command != locked_command_) {
            board_.diag_pulse(DiagLine::SecurityDrop, kDropPulse);
            disarm();
            return nack(rx, MessageType::OperateNack, Error::CommandMismatch);
        }

        // Токен анулюємо ДО звертання до приводу: дубль кадру вже не пройде,
        // навіть якщо привід відпрацьовує довго.
        const CommandCode cmd = locked_command_;
        active_token_ = Token{};
        state_        = State::Executing;
        board_.diag_level(DiagLine::Armed, false);

        const bool ok = board_.execute(cmd, rx.data());

        state_          = State::Idle;
        locked_command_ = CommandCode{};
        locked_source_  = NodeId{};
        arm_expiry_     = TimePoint{};

        if (!ok) {
            return nack(rx, MessageType::OperateNack, Error::InternalFault);
        }
        board_.diag_pulse(DiagLine::OperateExec, kExecPulse);
        ++exec_count_;
        return response(rx, MessageType::OperateAck);
    }

    case MessageType::CancelReq: {
        if (state_ == State::Executing ||
            (state_ == State::Armed && locked_source_ != rx.source)) {
            return nack(rx, MessageType::CancelNack, Error::Busy);
        }
        disarm();
        return response(rx, MessageType::CancelAck);
    }

    default:
        // Квитанції приймає пульт, не борт.
        return std::unexpected(Error::UnknownType);
    }
}

std::expected<std::span<std::uint8_t>, Error>
TargetEngine::handle_wire(std::span<const std::uint8_t> in, std::span<std::uint8_t> out,
                          TimePoint now) noexcept {
    const auto rx = decode(in);
    if (!rx) {
        return std::unexpected(rx.error());   // побитий ефіром кадр далі не йде
    }
    const auto tx = process(*rx, now);
    if (!tx) {
        return std::unexpected(tx.error());
    }
    return encode(*tx, out);
}

}  // namespace sbo
