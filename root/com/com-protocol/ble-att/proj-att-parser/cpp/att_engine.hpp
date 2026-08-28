// att_engine.hpp
#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <variant>
#include <expected>
#include <chrono>
#include <algorithm>

namespace ble::att {

using namespace std::chrono_literals;

constexpr uint16_t DefaultMtu = 23;
constexpr uint16_t MaxMtu     = 517;
constexpr auto TransactionTimeout = 30s;

enum class Opcode : uint8_t {
    ErrorRsp          = 0x01,
    ExchangeMtuReq    = 0x02,
    ExchangeMtuRsp    = 0x03,
    ReadReq           = 0x0A,
    ReadRsp           = 0x0B,
    WriteReq          = 0x12,
    WriteRsp          = 0x13,
    WriteCmd          = 0x52,
    HandleValueNtf    = 0x1B,
    HandleValueInd    = 0x1D,
    HandleValueCfm    = 0x1E
};

enum class ParseError {
    BufferTooShort,
    InvalidOpcode,
    InvalidLength,
    InvalidHandle,
    MtuTooSmall
};

struct ErrorResponse {
    uint8_t  requestOpcode;
    uint16_t attributeHandle;
    uint8_t  errorCode;
};

struct ExchangeMtuResponse {
    uint16_t serverRxMtu;
};

struct ReadResponse {
    std::span<const uint8_t> value;
};

struct WriteResponse {};

struct Notification {
    uint16_t handle;
    std::span<const uint8_t> value;
};

using Packet = std::variant<
    ErrorResponse,
    ExchangeMtuResponse,
    ReadResponse,
    WriteResponse,
    Notification
>;

class PacketParser {
public:
    static std::expected<Packet, ParseError> parse(std::span<const uint8_t> buffer) noexcept {
        if (buffer.empty()) {
            return std::unexpected(ParseError::BufferTooShort);
        }

        const auto op = static_cast<Opcode>(buffer[0]);
        switch (op) {
            case Opcode::ErrorRsp: {
                if (buffer.size() != 5) return std::unexpected(ParseError::InvalidLength);
                return ErrorResponse{
                    .requestOpcode   = buffer[1],
                    .attributeHandle = readLe16(buffer.subspan<2, 2>()),
                    .errorCode       = buffer[4]
                };
            }
            case Opcode::ExchangeMtuRsp: {
                if (buffer.size() != 3) return std::unexpected(ParseError::InvalidLength);
                const uint16_t mtu = readLe16(buffer.subspan<1, 2>());
                if (mtu < DefaultMtu) return std::unexpected(ParseError::MtuTooSmall);
                return ExchangeMtuResponse{ .serverRxMtu = mtu };
            }
            case Opcode::ReadRsp: {
                return ReadResponse{ .value = buffer.subspan(1) };
            }
            case Opcode::WriteRsp: {
                if (buffer.size() != 1) return std::unexpected(ParseError::InvalidLength);
                return WriteResponse{};
            }
            case Opcode::HandleValueNtf: {
                if (buffer.size() < 3) return std::unexpected(ParseError::InvalidLength);
                const uint16_t hdl = readLe16(buffer.subspan<1, 2>());
                if (hdl == 0) return std::unexpected(ParseError::InvalidHandle);
                return Notification{
                    .handle = hdl,
                    .value  = buffer.subspan(3)
                };
            }
            default:
                return std::unexpected(ParseError::InvalidOpcode);
        }
    }

private:
    template <size_t Offset, size_t Count>
    static constexpr uint16_t readLe16(std::span<const uint8_t, Count> s) noexcept {
        return static_cast<uint16_t>(s[0]) | (static_cast<uint16_t>(s[1]) << 8);
    }

    static constexpr uint16_t readLe16(std::span<const uint8_t, 2> s) noexcept {
        return static_cast<uint16_t>(s[0]) | (static_cast<uint16_t>(s[1]) << 8);
    }
};

class ClientStateMachine {
public:
    enum class State { Idle, WaitingResponse, TimedOut };

    [[nodiscard]] bool canSendRequest() const noexcept {
        return state_ == State::Idle;
    }

    bool startRequest(Opcode reqOp, uint16_t handle,
                      std::chrono::steady_clock::time_point now) noexcept {
        if (state_ != State::Idle) return false;
        pendingOp_     = reqOp;
        pendingHandle_ = handle;
        timerStart_    = now;
        state_         = State::WaitingResponse;
        return true;
    }

    bool onPacketReceived(const Packet& pkt) noexcept {
        if (std::holds_alternative<Notification>(pkt)) {
            return true; // Сповіщення приймаються без розблокування черги
        }

        if (state_ == State::WaitingResponse) {
            bool matched = std::visit([this](const auto& p) {
                using T = std::decay_t<decltype(p)>;
                if constexpr (std::is_same_v<T, ErrorResponse>) {
                    return static_cast<uint8_t>(pendingOp_) == p.requestOpcode;
                } else if constexpr (std::is_same_v<T, ReadResponse>) {
                    return pendingOp_ == Opcode::ReadReq;
                } else if constexpr (std::is_same_v<T, WriteResponse>) {
                    return pendingOp_ == Opcode::WriteReq;
                } else if constexpr (std::is_same_v<T, ExchangeMtuResponse>) {
                    effectiveMtu_ = std::min(p.serverRxMtu, MaxMtu);
                    return pendingOp_ == Opcode::ExchangeMtuReq;
                }
                return false;
            }, pkt);

            if (matched) {
                state_ = State::Idle;
                pendingOp_ = {};
                pendingHandle_ = 0;
                return true;
            }
        }
        return false;
    }

    bool checkTimeout(std::chrono::steady_clock::time_point now) noexcept {
        if (state_ == State::WaitingResponse) {
            if (now - timerStart_ >= TransactionTimeout) {
                state_ = State::TimedOut;
                return true;
            }
        }
        return false;
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint16_t effectiveMtu() const noexcept { return effectiveMtu_; }

private:
    State state_{State::Idle};
    Opcode pendingOp_{};
    uint16_t pendingHandle_{0};
    uint16_t effectiveMtu_{DefaultMtu};
    std::chrono::steady_clock::time_point timerStart_{};
};

} // namespace ble::att
