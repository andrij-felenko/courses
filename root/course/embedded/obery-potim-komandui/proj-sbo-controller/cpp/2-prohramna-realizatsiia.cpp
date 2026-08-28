// sbo_target_engine.hpp — Ідіоматичний C++20 з суворою типізацією
#include <cstdint>
#include <chrono>
#include <optional>
#include <expected>
#include <span>
#include <array>
#include <concepts>

namespace sbo {

using namespace std::chrono_literals;

enum class State : uint8_t {
    Idle = 0,
    Armed,
    Executing
};

enum class MessageType : uint8_t {
    SelectReq   = 0x10,
    SelectAck   = 0x11,
    SelectNack  = 0x12,
    OperateReq  = 0x20,
    OperateAck  = 0x21,
    OperateNack = 0x22,
    CancelReq   = 0x30,
    CancelAck   = 0x31
};

enum class Error : uint8_t {
    Busy = 1,
    InvalidToken,
    TimeoutExpired,
    NotArmed,
    CommandMismatch,
    BroadcastForbidden,
    InternalFault
};

struct NodeId {
    uint8_t value;
    constexpr explicit NodeId(uint8_t v) : value(v) {}
    constexpr bool is_broadcast() const noexcept { return value == 0xFF; }
    constexpr auto operator<=>(const NodeId&) const = default;
};

struct Token {
    uint32_t value{0};
    constexpr explicit Token(uint32_t v) : value(v) {}
    constexpr bool is_valid() const noexcept { return value != 0; }
    constexpr auto operator<=>(const Token&) const = default;
};

struct CommandCode {
    uint16_t value{0};
    constexpr explicit CommandCode(uint16_t v) : value(v) {}
    constexpr auto operator<=>(const CommandCode&) const = default;
};

struct Packet {
    uint8_t magic{0x5B};
    uint8_t seq{0};
    MessageType type{MessageType::SelectReq};
    NodeId source{0};
    NodeId target{0};
    State state{State::Idle};
    Token token{0};
    CommandCode command{0};
    std::chrono::milliseconds timeout{5000};
    std::array<uint8_t, 64> payload{};
    size_t payload_len{0};
};

class TargetEngine {
public:
    using TimePoint = std::chrono::steady_clock::time_point;

    explicit TargetEngine(NodeId self_id) noexcept 
        : self_id_(self_id) {}

    void tick(TimePoint now) noexcept {
        if (state_ == State::Armed && now >= arm_expiry_) {
            disarm();
        }
    }

    [[nodiscard]] std::expected<Packet, Error> process_packet(const Packet& rx, TimePoint now) noexcept {
        if (rx.target.is_broadcast()) {
            return std::unexpected(Error::BroadcastForbidden);
        }
        if (rx.target != self_id_) {
            return std::unexpected(Error::InternalFault);
        }

        tick(now);

        Packet tx{};
        tx.magic = 0x5B;
        tx.seq = rx.seq;
        tx.source = self_id_;
        tx.target = rx.source;
        tx.command = rx.command;

        switch (rx.type) {
            case MessageType::SelectReq: {
                if (state_ == State::Armed && locked_source_ != rx.source) {
                    tx.type = MessageType::SelectNack;
                    tx.state = state_;
                    tx.payload[0] = static_cast<uint8_t>(Error::Busy);
                    tx.payload_len = 1;
                    return tx;
                }

                state_ = State::Armed;
                locked_source_ = rx.source;
                locked_command_ = rx.command;
                active_token_ = generate_token();
                arm_expiry_ = now + rx.timeout;

                tx.type = MessageType::SelectAck;
                tx.state = State::Armed;
                tx.token = active_token_;
                tx.timeout = rx.timeout;
                return tx;
            }

            case MessageType::OperateReq: {
                if (state_ != State::Armed) {
                    tx.type = MessageType::OperateNack;
                    tx.state = state_;
                    tx.payload[0] = static_cast<uint8_t>(Error::NotArmed);
                    tx.payload_len = 1;
                    return tx;
                }

                if (rx.token != active_token_) {
                    disarm();
                    tx.type = MessageType::OperateNack;
                    tx.state = State::Idle;
                    tx.payload[0] = static_cast<uint8_t>(Error::InvalidToken);
                    tx.payload_len = 1;
                    return tx;
                }

                if (rx.command != locked_command_) {
                    disarm();
                    tx.type = MessageType::OperateNack;
                    tx.state = State::Idle;
                    tx.payload[0] = static_cast<uint8_t>(Error::CommandMismatch);
                    tx.payload_len = 1;
                    return tx;
                }

                disarm(); // Одноразове виконання
                tx.type = MessageType::OperateAck;
                tx.state = State::Idle;
                return tx;
            }

            case MessageType::CancelReq: {
                disarm();
                tx.type = MessageType::CancelAck;
                tx.state = State::Idle;
                return tx;
            }

            default:
                return std::unexpected(Error::InternalFault);
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] NodeId id() const noexcept { return self_id_; }

private:
    void disarm() noexcept {
        state_ = State::Idle;
        active_token_ = Token{0};
        locked_command_ = CommandCode{0};
        locked_source_ = NodeId{0};
    }

    Token generate_token() noexcept {
        prng_seed_ = prng_seed_ * 1664525u + 1013904223u;
        return Token{prng_seed_ == 0 ? 0xA5A55A5Au : prng_seed_};
    }

    NodeId self_id_;
    State state_{State::Idle};
    NodeId locked_source_{0};
    CommandCode locked_command_{0};
    Token active_token_{0};
    TimePoint arm_expiry_{};
    uint32_t prng_seed_{0x12345678};
};

} // namespace sbo
