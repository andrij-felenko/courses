class TokenBucketLimiter {
public:
    explicit TokenBucketLimiter(uint64_t bytes_per_sec)
        : rate_bytes_per_sec_(bytes_per_sec),
          available_tokens_(bytes_per_sec),
          last_refill_time_(get_monotonic_time_ns()) {}

    void throttle(uint64_t bytes_to_send) {
        refill();
        while (available_tokens_ < bytes_to_send) {
            uint64_t missing = bytes_to_send - available_tokens_;
            uint64_t sleep_ns = (missing * 1'000'000'000ULL) / rate_bytes_per_sec_;
            sleep_nanoseconds(sleep_ns);
            refill();
        }
        available_tokens_ -= bytes_to_send;
    }

private:
    void refill() {
        uint64_t now = get_monotonic_time_ns();
        uint64_t elapsed_ns = now - last_refill_time_;
        uint64_t added_tokens = (elapsed_ns * rate_bytes_per_sec_) / 1'000'000'000ULL;
        if (added_tokens > 0) {
            available_tokens_ = std::min(available_tokens_ + added_tokens, rate_bytes_per_sec_);
            last_refill_time_ = now;
        }
    }

    uint64_t rate_bytes_per_sec_;
    uint64_t available_tokens_;
    uint64_t last_refill_time_;
};
