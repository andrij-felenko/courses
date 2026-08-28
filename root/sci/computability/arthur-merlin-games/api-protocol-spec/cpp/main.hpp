#ifndef ARTHUR_MERLIN_SPEC_HPP
#define ARTHUR_MERLIN_SPEC_HPP

#include <vector>
#include <cstdint>
#include <cstddef>
#include <string>
#include <functional>
#include <memory>
#include <chrono>
#include <system_error>

namespace am_protocol {

enum class State : uint8_t {
    Uninitialized = 0,
    Ready,
    WaitingResponse,
    Verifying,
    Accepted,
    Rejected,
    Aborted
};

enum class ErrorCode : int {
    Success = 0,
    InvalidParam = -1,
    EntropyFailure = -2,
    BufferOverflow = -3,
    Timeout = -4,
    VerificationFailed = -5,
    StateMismatch = -6
};

/* Спеціалізована категорія помилок C++ std::error_category */
class ProtocolErrorCategory : public std::error_category {
public:
    const char* name() const noexcept override { return "ArthurMerlinProtocol"; }
    std::string message(int ev) const override {
        switch (static_cast<ErrorCode>(ev)) {
            case ErrorCode::Success: return "Успішне виконання";
            case ErrorCode::InvalidParam: return "Недійсний параметр конфігурації";
            case ErrorCode::EntropyFailure: return "Збій генератора випадкових монет";
            case ErrorCode::BufferOverflow: return "Переповнення буфера доказу";
            case ErrorCode::Timeout: return "Перевищено часовий ліміт очікування відповіді";
            case ErrorCode::VerificationFailed: return "Перевірка предиката повернула помилку";
            case ErrorCode::StateMismatch: return "Некоректний стан автомата сесії";
            default: return "Невідома помилка протоколу";
        }
    }
};

struct Config {
    std::size_t total_rounds{10};
    std::size_t coin_bits_per_round{256};
    std::size_t max_message_size{4096};
    double target_soundness{1e-6};
    std::chrono::milliseconds timeout{1000};
    bool enable_logging{false};
};

struct ChallengeEnvelope {
    std::uint32_t round_index{0};
    std::chrono::nanoseconds timestamp;
    std::vector<std::uint8_t> coin_bytes;
};

struct ResponseEnvelope {
    std::uint32_t round_index{0};
    std::vector<std::uint8_t> proof_bytes;
    std::chrono::microseconds execution_time;
};

using VerifierPredicate = std::function<bool(const ChallengeEnvelope&, const ResponseEnvelope&)>;

class VerifierSession {
public:
    explicit VerifierSession(const Config& config);
    ~VerifierSession() = default;

    VerifierSession(const VerifierSession&) = delete;
    VerifierSession& operator=(const VerifierSession&) = delete;

    VerifierSession(VerifierSession&&) noexcept = default;
    VerifierSession& operator=(VerifierSession&&) noexcept = default;

    ChallengeEnvelope generate_challenge();
    State process_and_verify(const ResponseEnvelope& response, const VerifierPredicate& predicate);

    [[nodiscard]] State state() const noexcept { return current_state_; }
    [[nodiscard]] std::size_t current_round() const noexcept { return current_round_; }
    [[nodiscard]] double current_soundness() const noexcept;

private:
    Config config_;
    State current_state_{State::Ready};
    std::size_t current_round_{0};
    std::size_t successful_rounds_{0};
    ChallengeEnvelope active_challenge_;
};

} // namespace am_protocol

#endif /* ARTHUR_MERLIN_SPEC_HPP */
