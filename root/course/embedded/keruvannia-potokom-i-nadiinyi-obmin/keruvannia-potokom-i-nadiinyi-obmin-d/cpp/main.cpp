#include <cstdint>
#include <algorithm>

class TokenBucketLimiter {
public:
    constexpr TokenBucketLimiter(uint32_t rate_bytes_per_sec, uint32_t capacity, uint32_t now_ms) noexcept
        : rate_{rate_bytes_per_sec}, capacity_{capacity}, tokens_{capacity}, last_update_ms_{now_ms} {}

    [[nodiscard]] bool try_consume(uint32_t size_bytes, uint32_t now_ms) noexcept {
        update(now_ms);
        if (tokens_ >= size_bytes) {
            tokens_ -= size_bytes;
            return true;
        }
        return false;
    }

    [[nodiscard]] uint32_t available_tokens(uint32_t now_ms) noexcept {
        update(now_ms);
        return tokens_;
    }

private:
    void update(uint32_t now_ms) noexcept {
        const uint32_t delta_ms = now_ms - last_update_ms_;
        if (delta_ms > 0) {
            const auto new_tokens = static_cast<uint32_t>((static_cast<uint64_t>(delta_ms) * rate_) / 1000ULL);
            if (new_tokens > 0) {
                tokens_ = std::min(capacity_, tokens_ + new_tokens);
                last_update_ms_ = now_ms;
            }
        }
    }

    uint32_t rate_{0};
    uint32_t capacity_{0};
    uint32_t tokens_{0};
    uint32_t last_update_ms_{0};
};
