#include <array>
#include <cstdint>
#include <algorithm>

template <std::size_t NumWords = 16>
class LargeAntiReplayFilter {
public:
    static constexpr std::size_t TotalBits = NumWords * 64;

    LargeAntiReplayFilter() noexcept {
        window_.fill(0);
    }

    [[nodiscard]] bool process(uint64_t seq) noexcept {
        if (seq > max_seq_) {
            const uint64_t diff = seq - max_seq_;
            if (diff < TotalBits) {
                const std::size_t words_shift = diff / 64;
                const std::size_t bits_shift = diff % 64;

                for (std::size_t i = NumWords; i-- > 0;) {
                    uint64_t src = (i >= words_shift) ? window_[i - words_shift] : 0ULL;
                    uint64_t prev = (i > words_shift && bits_shift > 0) ? window_[i - words_shift - 1] : 0ULL;
                    window_[i] = (src << bits_shift) | (bits_shift > 0 ? (prev >> (64 - bits_shift)) : 0ULL);
                }
                window_[0] |= 1ULL;
            } else {
                window_.fill(0);
                window_[0] = 1ULL;
            }
            max_seq_ = seq;
            return true;
        }

        const uint64_t diff = max_seq_ - seq;
        if (diff >= TotalBits) {
            return false;
        }

        const std::size_t word_idx = diff / 64;
        const std::size_t bit_idx = diff % 64;
        const uint64_t mask = 1ULL << bit_idx;

        if ((window_[word_idx] & mask) != 0) {
            return false;
        }

        window_[word_idx] |= mask;
        return true;
    }

private:
    uint64_t max_seq_{0};
    std::array<uint64_t, NumWords> window_{};
};
