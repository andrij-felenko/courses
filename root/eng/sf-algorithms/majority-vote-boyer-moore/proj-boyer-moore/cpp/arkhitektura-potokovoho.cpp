#include <concepts>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

template <std::equality_comparable T>
class MajorityVoteAccumulator {
public:
    constexpr MajorityVoteAccumulator() noexcept = default;

    constexpr void update(const T& value) noexcept {
        if (count_ == 0) {
            candidate_ = value;
            count_ = 1;
        } else if (candidate_ == value) {
            ++count_;
        } else {
            --count_;
        }
    }

    [[nodiscard]] constexpr std::optional<T> candidate() const noexcept {
        if (count_ > 0) {
            return candidate_;
        }
        return std::nullopt;
    }

    [[nodiscard]] constexpr std::size_t surplus() const noexcept {
        return count_;
    }

    constexpr void reset() noexcept {
        candidate_ = T{};
        count_ = 0;
    }

private:
    T candidate_{};
    std::size_t count_{0};
};

template <std::equality_comparable T>
[[nodiscard]] std::optional<T> find_majority_element(std::span<const T> data) noexcept {
    if (data.empty()) {
        return std::nullopt;
    }

    MajorityVoteAccumulator<T> tracker;
    for (const auto& item : data) {
        tracker.update(item);
    }

    const auto cand = tracker.candidate();
    if (!cand.has_value()) {
        return std::nullopt;
    }

    std::size_t actual_count = 0;
    for (const auto& item : data) {
        if (item == *cand) {
            ++actual_count;
        }
    }

    if (actual_count > data.size() / 2) {
        return cand;
    }

    return std::nullopt;
}
