#include <string>
#include <string_view>
#include <optional>
#include <variant>
#include <expected>
#include <chrono>
#include <random>
#include <algorithm>
#include <cstdint>

enum class OpState : uint8_t {
    Pending = 0,
    Running,
    Succeeded,
    Failed,
    Cancelled
};

struct ProblemDetails {
    std::string type;
    std::string title;
    int status_code{500};
    std::string detail;
};

enum class FsmError {
    InvalidTransition,
    LeaseExpired,
    InvalidLeaseToken,
    AlreadyTerminal
};

class LongRunningOpContext {
public:
    using TimePoint = std::chrono::time_point<std::chrono::system_clock>;
    using Duration = std::chrono::seconds;

    explicit LongRunningOpContext(std::string op_id, std::string idem_key, TimePoint now)
        : op_id_(std::move(op_id)),
          idempotency_key_(std::move(idem_key)),
          state_(OpState::Pending),
          progress_(0.0f),
          attempt_count_(0),
          lease_token_(0),
          created_at_(now),
          updated_at_(now),
          lease_expires_at_(now),
          cancel_requested_(false) {}

    [[nodiscard]] OpState state() const noexcept { return state_; }
    [[nodiscard]] float progress() const noexcept { return progress_; }
    [[nodiscard]] std::string_view operation_id() const noexcept { return op_id_; }
    [[nodiscard]] std::string_view idempotency_key() const noexcept { return idempotency_key_; }
    [[nodiscard]] std::string_view result_url() const noexcept { return result_url_; }
    [[nodiscard]] bool is_cancel_requested() const noexcept { return cancel_requested_; }

    void request_cancellation() noexcept {
        cancel_requested_ = true;
    }

    [[nodiscard]] static bool can_transition(OpState from, OpState to) noexcept {
        switch (from) {
            case OpState::Pending:
                return (to == OpState::Running || to == OpState::Cancelled || to == OpState::Failed);
            case OpState::Running:
                return (to == OpState::Succeeded || to == OpState::Failed || 
                        to == OpState::Cancelled || to == OpState::Pending);
            case OpState::Succeeded:
            case OpState::Failed:
            case OpState::Cancelled:
                return false;
            default:
                return false;
        }
    }

    std::expected<void, FsmError> claim_lease(uint64_t worker_token, Duration lease_dur, TimePoint now) noexcept {
        const bool is_pending = (state_ == OpState::Pending);
        const bool is_expired = (state_ == OpState::Running && lease_expires_at_ < now);

        if (!is_pending && !is_expired) {
            return std::unexpected(FsmError::InvalidTransition);
        }

        if (!can_transition(state_, OpState::Running)) {
            return std::unexpected(FsmError::InvalidTransition);
        }

        state_ = OpState::Running;
        lease_token_ = worker_token;
        lease_expires_at_ = now + lease_dur;
        ++attempt_count_;
        updated_at_ = now;
        return {};
    }

    std::expected<void, FsmError> heartbeat(uint64_t worker_token, float prog, Duration lease_ext, TimePoint now) noexcept {
        if (state_ != OpState::Running) return std::unexpected(FsmError::InvalidTransition);
        if (lease_token_ != worker_token) return std::unexpected(FsmError::InvalidLeaseToken);
        if (lease_expires_at_ < now) return std::unexpected(FsmError::LeaseExpired);

        lease_expires_at_ = now + lease_ext;
        progress_ = std::clamp(prog, 0.0f, 1.0f);
        updated_at_ = now;
        return {};
    }

    std::expected<void, FsmError> complete_success(uint64_t worker_token, std::string_view res_url, TimePoint now) {
        if (state_ != OpState::Running) return std::unexpected(FsmError::InvalidTransition);
        if (lease_token_ != worker_token) return std::unexpected(FsmError::InvalidLeaseToken);
        if (lease_expires_at_ < now) return std::unexpected(FsmError::LeaseExpired);

        if (!can_transition(state_, OpState::Succeeded)) {
            return std::unexpected(FsmError::InvalidTransition);
        }

        state_ = OpState::Succeeded;
        progress_ = 1.0f;
        result_url_ = res_url;
        updated_at_ = now;
        return {};
    }

    std::expected<void, FsmError> complete_failure(uint64_t worker_token, ProblemDetails err, TimePoint now) {
        if (state_ != OpState::Running) return std::unexpected(FsmError::InvalidTransition);
        if (lease_token_ != worker_token) return std::unexpected(FsmError::InvalidLeaseToken);

        if (!can_transition(state_, OpState::Failed)) {
            return std::unexpected(FsmError::InvalidTransition);
        }

        state_ = OpState::Failed;
        error_ = std::move(err);
        updated_at_ = now;
        return {};
    }

private:
    std::string op_id_;
    std::string idempotency_key_;
    OpState state_;
    float progress_;
    uint32_t attempt_count_;
    uint64_t lease_token_;
    TimePoint created_at_;
    TimePoint updated_at_;
    TimePoint lease_expires_at_;
    bool cancel_requested_;
    std::string result_url_;
    std::optional<ProblemDetails> error_;
};

/* Обчислення джитеру мовою C++20 */
class JitterBackoffCalculator {
public:
    explicit JitterBackoffCalculator(uint32_t base_sec = 1, uint32_t max_sec = 60)
        : base_sec_(base_sec), max_sec_(max_sec), rng_(std::random_device{}()) {}

    [[nodiscard]] std::chrono::seconds calculate(uint32_t attempt) {
        const uint32_t shift = std::min(attempt, 20u);
        const uint64_t raw = static_cast<uint64_t>(base_sec_) << shift;
        const uint32_t capped = static_cast<uint32_t>(std::min<uint64_t>(raw, max_sec_));
        if (capped == 0) return std::chrono::seconds(0);

        std::uniform_int_distribution<uint32_t> dist(0, capped);
        return std::chrono::seconds(dist(rng_));
    }

private:
    uint32_t base_sec_;
    uint32_t max_sec_;
    std::mt19937 rng_;
};
