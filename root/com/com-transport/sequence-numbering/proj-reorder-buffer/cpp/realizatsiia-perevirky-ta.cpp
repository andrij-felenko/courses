#include <cstdint>
#include <concepts>
#include <bitset>

template <std::size_t WindowSize = 64>
requires (WindowSize > 0 && WindowSize <= 128)
class AntiReplayWindow {
public:
    constexpr AntiReplayWindow() noexcept = default;

    [[nodiscard]] constexpr bool check(std::uint64_t seq) const noexcept {
        if (!initialized_) {
            return true;
        }
        if (seq > top_seq_) {
            return true;
        }
        const std::uint64_t diff = top_seq_ - seq;
        if (diff >= WindowSize) {
            return false; // За межами вікна (stale)
        }
        return !bitmap_.test(diff);
    }

    constexpr void update(std::uint64_t seq) noexcept {
        if (!initialized_) {
            top_seq_ = seq;
            bitmap_.set(0);
            initialized_ = true;
            return;
        }

        if (seq > top_seq_) {
            const std::uint64_t shift = seq - top_seq_;
            if (shift < WindowSize) {
                bitmap_ <<= shift;
                bitmap_.set(0);
            } else {
                bitmap_.reset();
                bitmap_.set(0);
            }
            top_seq_ = seq;
        } else {
            const std::uint64_t diff = top_seq_ - seq;
            if (diff < WindowSize) {
                bitmap_.set(diff);
            }
        }
    }

    constexpr void reset() noexcept {
        top_seq_ = 0;
        bitmap_.reset();
        initialized_ = false;
    }

    [[nodiscard]] constexpr std::uint64_t top_sequence() const noexcept {
        return top_seq_;
    }

private:
    std::uint64_t top_seq_{0};
    std::bitset<WindowSize> bitmap_{};
    bool initialized_{false};
};
