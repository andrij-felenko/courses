// sbo_core.hpp — Безпечна типізована реалізація стандарту C++20
#include <cstdint>
#include <chrono>
#include <optional>
#include <expected>

namespace safety {

using namespace std::chrono_literals;

enum class State : uint8_t {
    Idle = 0,
    Armed,
    Executed
};

enum class GateError : uint8_t {
    Expired = 1,
    TokenMismatch,
    CommandMismatch,
    NotArmed
};

class SboGate {
public:
    using TimePoint = std::chrono::steady_clock::time_point;

    explicit constexpr SboGate(uint8_t self_id) noexcept 
        : self_id_(self_id) {}

    void arm(uint16_t cmd, uint32_t token, std::chrono::milliseconds window, TimePoint now) noexcept {
        state_ = State::Armed;
        active_token_ = token;
        expected_cmd_ = cmd;
        deadline_ = now + window;
    }

    [[nodiscard]] std::expected<void, GateError> verify_and_consume(uint16_t cmd, uint32_t token, TimePoint now) noexcept {
        if (state_ != State::Armed) {
            return std::unexpected(GateError::NotArmed);
        }
        if (now >= deadline_) {
            disarm();
            return std::unexpected(GateError::Expired);
        }
        if (token != active_token_) {
            disarm();
            return std::unexpected(GateError::TokenMismatch);
        }
        if (cmd != expected_cmd_) {
            disarm();
            return std::unexpected(GateError::CommandMismatch);
        }

        disarm(); // Одноразовий селектор
        return {};
    }

    void tick(TimePoint now) noexcept {
        if (state_ == State::Armed && now >= deadline_) {
            disarm();
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint8_t id() const noexcept { return self_id_; }

private:
    void disarm() noexcept {
        state_ = State::Idle;
        active_token_ = 0;
        expected_cmd_ = 0;
    }

    uint8_t self_id_;
    State state_{State::Idle};
    uint32_t active_token_{0};
    uint16_t expected_cmd_{0};
    TimePoint deadline_{};
};

} // namespace safety
