#include <cstdint>
#include <algorithm>

class RetryPolicy {
public:
    constexpr RetryPolicy(uint8_t max_attempts, uint32_t base_delay_us, 
                          uint32_t max_delay_us, uint32_t initial_seed) noexcept
        : max_attempts_(max_attempts),
          base_delay_us_(base_delay_us),
          max_delay_us_(max_delay_us),
          rand_seed_(initial_seed) {}

    [[nodiscard]] uint32_t calculate_delay_us(uint8_t attempt) noexcept {
        if (attempt == 0) return 0;

        const uint32_t shift = (attempt > 10) ? 10 : (attempt - 1);
        uint32_t exp_delay = base_delay_us_ * (1UL << shift);
        exp_delay = std::min(exp_delay, max_delay_us_);

        const uint32_t half = exp_delay / 2;
        const uint32_t jitter = next_random() % (half + 1);
        return half + jitter;
    }

    [[nodiscard]] constexpr uint8_t max_attempts() const noexcept {
        return max_attempts_;
    }

private:
    uint32_t next_random() noexcept {
        rand_seed_ = (rand_seed_ * 1664525UL + 1013904223UL);
        return rand_seed_;
    }

    uint8_t  max_attempts_{3};
    uint32_t base_delay_us_{1000};
    uint32_t max_delay_us_{16000};
    uint32_t rand_seed_{1234567};
};
