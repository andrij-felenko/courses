#include <cstdint>
#include <string>
#include <string_view>
#include <memory>
#include <optional>
#include <chrono>

struct RequestContext {
    std::string_view idempotency_key;
    std::string_view nonce;
    std::string_view signature;
    std::chrono::system_clock::time_point timestamp;
    uint64_t fencing_token{0};
    std::string_view request_body;
};

enum class ValidationDecision {
    AllowFirstTime,
    ServeCachedResponse,
    RejectDuplicateInFlight,
    RejectExpiredTimestamp,
    RejectInvalidSignature,
    RejectStaleFencingToken
};

struct InterceptorResult {
    ValidationDecision decision;
    std::optional<std::string> cached_payload;
    int http_status_code{200};
    std::string error_message;
};

class IReplayProtectionInterceptor {
public:
    virtual ~IReplayProtectionInterceptor() = default;

    // Попередня перевірка до виклику доменної логіки
    [[nodiscard]] virtual InterceptorResult pre_handle(const RequestContext& ctx) = 0;

    // Фіксація успішного результату для ідемпотентних повторів
    virtual void post_handle_success(
        std::string_view idempotency_key,
        int status_code,
        std::string_view response_body
    ) = 0;

    // Скасування блокування при внутрішній системній помилці
    virtual void post_handle_failure(std::string_view idempotency_key) = 0;
};
